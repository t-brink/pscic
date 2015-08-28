import math
from pyparsing import (Word, oneOf, Literal, CaselessLiteral, Regex,
                       Optional, Suppress, Forward, FollowedBy, Group,
                       OneOrMore, ZeroOrMore,
                       nums, alphas, ParseResults)

from . import operators

# Definitions. #########################################################
# Identifier, must start with unicode letter, can then contain unicode
# letter, unicode number, or underscore.
identifier = Regex(r'[^\W\d_]\w*')

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


# Expression ###########################################################
expr = Forward()

# Term.
lpar = Suppress('(')
rpar = Suppress(')')
term = operand | ( lpar + expr + rpar )

# Function.
# TODO: multiple args separated by comma/semicolon(which one?)
#                  pro                contra
#     comma:   easy, nice look     usage as decimal point, thousand separator
# semicolon:   no other usage      harder to type
func_term = Forward()
func_expr = Group( identifier + lpar + func_term + rpar )
func_expr.setParseAction(operators.Function.process)
func_term <<= ( func_expr | term )

# Factorial
fact_expr = Group( func_term + OneOrMore(factop) )
fact_expr.setParseAction(operators.PostfixSymbol.process)
fact_term = ( fact_expr | func_term )

# Exponent
exp_term = Forward()
# 'signop' in exponent is handled in process_expop().
exp_expr = Group( fact_term + expop + ZeroOrMore(signop) + exp_term )
exp_expr.setParseAction(operators.Exponent.process)
exp_term <<= ( exp_expr | fact_term )

# Sign.
sign_term = Forward()
_signop = Optional(signop) # "try to avoid LR" was the original comment, dunno!?
sign_expr = FollowedBy(_signop.expr + sign_term) + Group( _signop + sign_term )
sign_expr.setParseAction(operators.PrefixSymbol.process)
sign_term <<= ( sign_expr | exp_term )

# Multiplication.
mult_expr = Group( sign_term + OneOrMore( multop + sign_term ) )
mult_expr.setParseAction(operators.InfixLeftSymbol.process)
mult_term = ( mult_expr | sign_term )

# Addition.
add_expr = Group( mult_term + OneOrMore( addop + mult_term ) )
add_expr.setParseAction(operators.InfixLeftSymbol.process)
add_term = ( add_expr | mult_term )

# Complete expression.
expr <<= add_term

def parse(string):
    tree = operators.Expression(expr.parseString(string, parseAll=True)[0])
    return tree
