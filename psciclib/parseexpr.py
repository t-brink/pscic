# Copyright (C) 2015, 2016  Tobias Brink
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

# Special symbols for currencies.
currency_symbols = oneOf("€ £ $ ₪ ¥ ￥ ₩ ￦ ฿ ₹")

# Identifier, must start with unicode letter, can then contain unicode
# letter, unicode number, or underscore.
identifier = currency_symbols | ( NotAny( keyword ) + Regex(r'[^\W\d_]\w*') )

# Operands
integer = Word(nums).setParseAction(operators.process_int)

float_ = Regex(r'''[0-9]+           # integer part
                   (?:
                       (?:          # optional decimal part followed by e-part
                           (?: \.[0-9]* )?
                           [eE]
                           [-\u2212+]?   # U+2212 is unicode minus
                           [0-9]+
                       )
                       |
                       (?: \.[0-9]* )  # mandatory decimal part without e-part
                   )''',
               re.VERBOSE)
float_.setParseAction(operators.process_float)

unicode_fraction = oneOf("½ ⅓ ¼ ⅕ ⅙ ⅐ ⅛ ⅑ ⅒ ⅔ ¾ ⅖ ⅗ ⅘ ⅚ ⅜ ⅝ ⅞")
unicode_fraction.setParseAction(operators.process_unicode_fraction)

hexint = Group( Literal("0x") + Regex(r'[0-9a-fA-F]+') )
hexint.setParseAction(operators.process_intbase)
octint = Group( Literal("0o") + Regex(r'[0-7]+') )
octint.setParseAction(operators.process_intbase)
binint = Group( Literal("0b") + Regex(r'[01]+') )
binint.setParseAction(operators.process_intbase)

romanint = Group(
    Literal("0r")
    + FollowedBy(
        # do not accept empty string!
        oneOf("I V X L C D M", caseless=True)
    )
    + Regex(r'M{0,4}', re.IGNORECASE)
    + Regex(r'CM|CD|D?C{0,4}', re.IGNORECASE)
    + Regex(r'XC|XL|L?X{0,4}', re.IGNORECASE)
    + Regex(r'IX|IV|V?I{0,4}', re.IGNORECASE)
)
romanint.setParseAction(operators.process_romanint)

hexreal = Group( Literal("0x") + Regex(r'[0-9a-fA-F]+')
                 + Literal(".") +  Regex(r'[0-9a-fA-F]+'))
hexreal.setParseAction(operators.process_realbase)
octreal = Group( Literal("0o") + Regex(r'[0-7]+')
                 + Literal(".") + Regex(r'[0-7]+') )
octreal.setParseAction(operators.process_realbase)
binreal = Group( Literal("0b") + Regex(r'[01]+')
                 + Literal(".") + Regex(r'[01]+') )
binreal.setParseAction(operators.process_realbase)

variable = identifier.copy()
variable.setParseAction(operators.Constant.process)

number = (
    float_ | unicode_fraction | hexreal | octreal | binreal
    | romanint
    | hexint | octint | binint | integer
)

operand = number | variable

# Operators
signop = oneOf("+ - \u2212") # last entry is unicode minus
addop = oneOf("+ - \u2212")
multop = oneOf("· * ÷ / //")
expop = oneOf("^ **")
factop = Literal("!")


# Expression ###########################################################
expr = Forward()

# Matrices and vectors.
matrix_sep = Suppress( Literal(",") )
matrix_rowsep = Suppress( Literal(";") )
matrix_row = Group( expr + ZeroOrMore( matrix_sep + expr ) )
matrix = Group(
    Suppress('[')
    + Optional( matrix_row + ZeroOrMore( matrix_rowsep + matrix_row ) )
    + Suppress(']')
)
matrix.setParseAction(operators.Matrix.process)

# Term.
lpar = Suppress('(')
rpar = Suppress(')')
term = operand | ( lpar + expr + rpar ) | matrix

# Function.
argsep = Suppress( oneOf(", ;") )
func_term = Forward()
func_expr = Group(
    identifier + lpar + expr + ZeroOrMore( argsep + expr ) + rpar
)
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
sm_exp_expr = Group( variable + expop + ZeroOrMore(signop) + exp_term )
sm_exp_expr.setParseAction(operators.Exponent.process)
signless_mult_expr = Group( sign_term + OneOrMore( sm_exp_expr | variable ) )
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
literal_one.setParseAction(operators.Unit.process_dimensionless)

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

equals_token = Literal("=")
equality = expr + equals_token + expr
equality.setParseAction(operators.Equality.process)

cmdln = conversion_cmd | equality | expr


# Support for unicode exponents by pre-processing.
def preprocess(string):
    """Replaces unicode exponents.

    WARNING: x²³ = x^(2^3) = x^8

    """
    return string.replace("¹", "^1") \
                 .replace("²", "^2") \
                 .replace("³", "^3") \
                 .replace("⁴", "^4") \
                 .replace("⁵", "^5") \
                 .replace("⁶", "^6") \
                 .replace("⁷", "^7") \
                 .replace("⁸", "^8") \
                 .replace("⁹", "^9") \
                 .replace("⁰", "^0")

# Parse it.
def parse(string):
    string = preprocess(string)
    return operators.Wrapper(
        string,
        cmdln.parseString(string, parseAll=True)[0]
    )
