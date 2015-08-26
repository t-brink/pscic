import math
from pyparsing import (Word, oneOf, Literal, CaselessLiteral, Regex,
                       Optional, Suppress, Forward, FollowedBy, Group,
                       OneOrMore, ZeroOrMore,
                       nums, alphas, ParseResults)

# Definitions. #########################################################
# Operands
integer = Word(nums).setParseAction(lambda t: int(t[0]))

pm = Literal('+') | Literal('-')
decimal_part = Literal(".") + Optional( Word(nums) )
exp_part = CaselessLiteral("e") + Optional( pm ) + Word(nums)
float_ = Word(nums) + ( (Optional(decimal_part) + exp_part) | decimal_part )
float_.setParseAction(lambda t: float("".join(t)))

operand = float_ | integer

# Operators
signop = oneOf("+ -")
addop = oneOf("+ -")
multop = oneOf("· * ÷ / //")
expop = oneOf("^ **")
factop = Literal("!")

# Identifier, must start with unicode letter, can then contain unicode
# letter, unicode number, or underscore.
identifier = Regex(r'[^\W\d_]\w*')


# Operator implementations #############################################
def sign_plus(op1):
    return op1

def sign_minus(op1):
    return -op1

def add(op1, op2):
    return op1 + op2

def subtract(op1, op2):
    return op1 - op2

def multiply(op1, op2):
    return op1 * op2

def divide(op1, op2):
    return op1 / op2

def intdivide(op1, op2):
    return int(op1 // op2)

def exponent(op1, op2):
    return op1 ** op2

def factorial(op1):
    return math.factorial(op1)


# Helper function ######################################################
# These convert all to prefix notation and replace the operator string
# by an actual function.  Some of these may be strings of operations,
# like 1 + 1 - 1; those will be converted to nested expressions like
# (1 + 1) - 1.
def process_signop(s, loc, toks):
    sign = toks[0][0]
    if sign == "+":
        toks[0][0] = sign_plus
    elif sign == "-":
        toks[0][0] = sign_minus
    return toks

def process_infix_left(s, loc, toks):
    l = list(reversed(toks[0])) # reverse, as append is faster than insert(0)
    while len(l) > 1:
        lhs = l.pop()
        op = l.pop()
        rhs = l.pop()
        # We will never get, e.g., +- mixed with */ due to the
        # parsing. Therefore it is fine to mix them wildly here
        # without error checking.
        if op == "+":
            fn = add
        elif op == "-":
            fn = subtract
        elif op == "*" or op == "·":
            fn = multiply
        elif op == "/" or op == "÷":
            fn = divide
        elif op == "//":
            fn = intdivide
        l.append(ParseResults([fn, lhs, rhs]))
    return ParseResults(l)

def process_expop(s, loc, toks):
    lhs = toks[0][0]
    toks[0][0] = exponent
    toks[0][1] = lhs
    # Find signs in exponent.
    signs = []
    while toks[0][2] in ("+", "-"):
        signs.append(toks[0].pop(2))
    if signs:
        signs.append(toks[0].pop())
        while len(signs) > 1:
            b = signs.pop()
            a = signs.pop()
            signs.append(process_signop(None, None, [ParseResults([a, b])])[0])
        toks[0].append(signs[0])
    return toks

def process_factop(s, loc, toks):
    l = list(reversed(toks[0])) # reverse, as append is faster than insert(0)
    while len(l) > 1:
        lhs = l.pop()
        op = l.pop()
        l.append(ParseResults([factorial, lhs]))
    return ParseResults(l)

def process_func(s, loc, toks):
    # TODO: Noop for now.
    toks[0][0] = lambda arg: arg
    return toks


# Expression ###########################################################
expr = Forward()

lpar = Suppress('(')
rpar = Suppress(')')
term = operand | ( lpar + expr + rpar )

# Factorial
fact_expr = Group( term + OneOrMore(factop) )
fact_expr.setParseAction(process_factop)
fact_term = ( fact_expr | term )

# Exponent
exp_term = Forward()
# 'signop' in exponent is handled in process_expop().
exp_expr = Group( fact_term + expop + ZeroOrMore(signop) + exp_term )
exp_expr.setParseAction(process_expop)
exp_term <<= ( exp_expr | fact_term )

# Sign.
sign_term = Forward()
_signop = Optional(signop) # "try to avoid LR" was the original comment, dunno!?
sign_expr = FollowedBy(_signop.expr + sign_term) + Group( _signop + sign_term )
sign_expr.setParseAction(process_signop)
sign_term <<= ( sign_expr | exp_term )

# Multiplication.
mult_expr = Group( sign_term + OneOrMore( multop + sign_term ) )
mult_expr.setParseAction(process_infix_left)
mult_term = ( mult_expr | sign_term )

# Addition.
add_expr = Group( mult_term + OneOrMore( addop + mult_term ) )
add_expr.setParseAction(process_infix_left)
add_term = ( add_expr | mult_term )

# Function.
# TODO: multiple args separated by comma/semicolon(which one?)
#                  pro                contra
#     comma:   easy, nice look     usage as decimal point, thousand separator
# semicolon:   no other usage      harder to type
func_expr = Group( identifier + lpar + add_term + rpar )
func_expr.setParseAction(process_func)
func_term = ( func_expr | add_term )

# Complete expression.
expr <<= func_term

def parse(string):
    return expr.parseString(string, parseAll=True)[0]
