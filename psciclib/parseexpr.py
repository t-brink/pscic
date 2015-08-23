import math
from pyparsing import (Word, oneOf, Literal, CaselessLiteral, Optional,
                       nums, alphas,
                       infixNotation, opAssoc, ParseResults)

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
multop = oneOf("* / //")
expop = oneOf("^ **")
factop = Literal("!")


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
        elif op == "*":
            fn = multiply
        elif op == "/":
            fn = divide
        elif op == "//":
            fn = intdivide
        l.append(ParseResults([fn, lhs, rhs]))
    return ParseResults(l)

def process_expop(s, loc, toks):
    lhs = toks[0][0]
    toks[0][0] = exponent
    toks[0][1] = lhs
    return toks

def process_factop(s, loc, toks):
    l = list(reversed(toks[0])) # reverse, as append is faster than insert(0)
    while len(l) > 1:
        lhs = l.pop()
        op = l.pop()
        l.append(ParseResults([factorial, lhs]))
    return ParseResults(l)

# Expression ###########################################################
expr = infixNotation(
    operand,
    [("!", 1, opAssoc.LEFT, process_factop),
     (expop, 2, opAssoc.RIGHT, process_expop),
     (signop, 1, opAssoc.RIGHT, process_signop),
     (multop, 2, opAssoc.LEFT, process_infix_left),
     (addop, 2, opAssoc.LEFT, process_infix_left)]
)


def parse(string):
    return expr.parseString(string, parseAll=True)[0]
