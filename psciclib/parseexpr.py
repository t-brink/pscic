# Copyright (C) 2015  Tobias Brink
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import re
import pyparsing
from pyparsing import (ParserElement, Word, oneOf, Literal, CaselessLiteral,
                       Regex, Optional, Suppress, Forward, FollowedBy, NotAny,
                       Group, OneOrMore, ZeroOrMore,
                       nums, alphas, ParseResults)
ParserElement.enablePackrat() # Significant speedup.

from . import operators
from .units import Q_

# Definitions. #########################################################

# These are reserved words that cannot be variables, constants, or units.
keyword = oneOf("to")

# Identifier, must start with unicode letter, can then contain unicode
# letter, unicode number, or underscore.
identifier = NotAny( keyword ) + Regex(r'[^\W\d_]\w*')

# Operands
integer = Word(nums).setParseAction(operators.process_int)

float_ = Regex(r'''[0-9]+           # integer part
                   (?:
                       (?:          # optional decimal part followed by e-part
                           (?: \.[0-9]* )?
                           [eE]
                           [-+]?
                           [0-9]+
                       )
                       |
                       (?: \.[0-9]* )  # mandatory decimal part without e-part
                   )''',
               re.VERBOSE)
float_.setParseAction(operators.process_float)

variable = identifier.copy()
variable.setParseAction(operators.Constant.process)

number = float_ | integer

operand = number | variable

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
func_expr = Group( identifier + lpar + expr + rpar )
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

# Multiplication without sign has precendence so that 2km / 3h means
# 2/3 km/h.  Multiplication without sign is possible if RHS is a
# variable/constant/unit.
signless_mult_expr = Group( sign_term + OneOrMore( variable ) )
signless_mult_expr.setParseAction(operators.InfixLeftSymbol.process)
signless_mult_term = ( signless_mult_expr | sign_term )

# Multiplication.
mult_expr = Group( signless_mult_term + OneOrMore(multop + signless_mult_term) )
mult_expr.setParseAction(operators.InfixLeftSymbol.process)
mult_term = ( mult_expr | signless_mult_term )

# Addition.
add_expr = Group( mult_term + OneOrMore( addop + mult_term ) )
add_expr.setParseAction(operators.InfixLeftSymbol.process)
add_term = ( add_expr | mult_term )

# Complete expression.
expr <<= add_term
expr.setParseAction(operators.Expression.process)


# A unit expression, containing only units. ############################
unit_expr = Forward()

single_unit = identifier.copy()
single_unit.setParseAction(operators.Unit.process)

literal_one = Literal("1")
literal_one.setParseAction(lambda _: Q_(1))

# The one allows for example for 1/h = h^-1.
unit_term = single_unit | literal_one | ( lpar + unit_expr + rpar )

# Exponent
unit_exp_term = Forward()
# 'signop' in exponent is handled in process_expop().
unit_exp_expr = Group( unit_term + expop + ZeroOrMore(signop) + exp_term )
unit_exp_expr.setParseAction(operators.Exponent.process)
unit_exp_term <<= ( unit_exp_expr | unit_term )

# Sign.
unit_sign_term = Forward()
unit_sign_expr = \
    FollowedBy(_signop.expr + unit_sign_term) + Group( _signop + unit_sign_term )
unit_sign_expr.setParseAction(operators.PrefixSymbol.process)
unit_sign_term <<= ( unit_sign_expr | unit_exp_term )

# Multiplication.
unit_mult_expr = Group( unit_sign_term + OneOrMore( multop + unit_sign_term ) )
unit_mult_expr.setParseAction(operators.InfixLeftSymbol.process)
unit_mult_term = ( unit_mult_expr | unit_sign_term )

unit_expr <<= unit_mult_term
unit_expr.setParseAction(operators.Expression.process)


# A command line (most often just an expression) #######################
to_token = Literal("to") + unit_expr

conversion_cmd = expr + to_token
conversion_cmd.setParseAction(operators.Conversion.process)

cmdln = conversion_cmd | expr


# Parse it.
def parse(string):
    return operators.Wrapper(cmdln.parseString(string, parseAll=True)[0])
