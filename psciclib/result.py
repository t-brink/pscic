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

"""Object to store the result of a calculation."""

import enum
import math
import collections

import sympy

from .units import Q_
from . import unitbridge


@enum.unique
class Mode(enum.Enum):
    try_exact = 1
    to_float = 2

@enum.unique
class NumeralSystem(enum.Enum):
    # The values are the bases and are used as that later (except for
    # "roman", obviuosly).
    binary = 2
    octal = 8
    decimal = 10
    hexadecimal = 16
    roman = 1001

@enum.unique
class UnitMode(enum.Enum):
    none = 0
    to_base = 1
    to_best = 2

_DEFAULT_DIGITS = 8


class RomanInt:

    numerals = ["I", "V", "X", "L", "C", "D", "M"]
    # Populate lookup table.
    table = {"": 0}
    rev_table = {0: ""} # int -> roman
    for exponent in range(3):
        one, five, ten = numerals[exponent*2:exponent*2+3]
        for i in range(1,10):
            val = i * 10**exponent
            rs = (i//5) * five + (i%5) * one
            table[rs] = val
            rev_table[val] = rs
            if i % 5 == 4:
                # subtraction
                rs = one + (1-i//5)*five + (i//5)*ten
                table[rs] = val
                rev_table[val] = rs # overwrite "sloppy" numerals, e.g. 'IIII'
    del exponent, one, five, ten, i, val, rs

    @classmethod
    def int_to_roman(cls, integer):
        # Check type.
        if isinstance(integer, (float, sympy.Float)) and (integer % 1 == 0):
            integer = int(integer)
        elif not (isinstance(integer, int) or integer.is_integer):
            raise ValueError("Roman numerals are only supported for integers.")
        # Check range.
        if integer < 1:
            retval = "-"
            integer = abs(integer)
        else:
            retval = ""
        if integer < 1 or integer > 4999:
            raise ValueError("Roman numerals are only supported on the "
                             "interval ±[1;4999]!")
        # Convert
        retval += "M" * (integer // 1000)
        integer %= 1000
        retval += cls.rev_table[(integer // 100) * 100]
        integer %= 100
        retval += cls.rev_table[(integer // 10) * 10]
        integer %= 10
        retval += cls.rev_table[integer]
        return retval


class Result:
    """
    Store the original input string, the parsed expression, and its result.
    """

    # What is the surrounding operation? Needed to decide if we need
    # parentheses.
    class _Surr(enum.Enum):
        none = 1 # no parentheses needed, ever
        addition = 2
        multiplication = 3
        exp_base = 4
        exp_exp = 5
        function_call = 6

    # This class stores some info for pretty-printing. It is used to
    # detect if we need parenthesis and to avoid nested <sup>.
    _Context = collections.namedtuple("_context",
                                      ["is_exponent", "surrounding_op"])

    def __init__(self, input_str, parsed, raw_result):
        self.input_str = input_str
        self.parsed = parsed
        self.raw_result = raw_result

    def n(self, except_classes=(bool, sympy.Integer, sympy.Float)):
        # TODO: this shares a bunch of code with the stuff below, I
        # guess. Need it for tests, though!
        if isinstance(self.raw_result, except_classes):
            # Those can be returned as-is.
            return self.raw_result
        elif isinstance(self.raw_result, sympy.Basic):
            # Those should be floatified.
            return self.raw_result.n()
        elif isinstance(self.raw_result, Solutions):
            # Rules as above for the individual solutions.
            return self.raw_result.apply(
                lambda sol: (sol
                             if isinstance(sol, except_classes)
                             else sol.n())
            )
        else:
            raise RuntimeError("Invalid type for Result.raw_result: {}"
                               "".format(type(self.raw_result)))

    @staticmethod
    def _to_float(obj, digits):
        if isinstance(obj, sympy.Integer):
            return obj
        else:
            return obj.evalf(n=digits)

    @staticmethod
    def _simplify(obj):
        if isinstance(obj, bool):
            return obj
        else:
            return obj.simplify()

    _hex_lookup = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                   "A", "B", "C", "D", "E", "F"]
    _base_conv = {NumeralSystem.binary: bin,
                  NumeralSystem.octal: oct,
                  NumeralSystem.hexadecimal: hex}
    @classmethod
    def _to_other_base(cls, obj, base, digits):
        conv = cls._base_conv[base]
        if isinstance(obj, sympy.Integer):
            return conv(obj)
        else:
            sign = "-" if obj < 0 else ""
            # Weird, but that way we do not lose precision.
            r = sympy.Rational(str(sympy.Abs(obj).evalf(10*digits)))
            numerator, denominator = int(r.p), int(r.q)
            # TODO: use uniform definition of the precision given by
            # `digits', here it is just number of digits after the
            # decimal point, which is not consistent!
            i = 0
            b = base.value
            l = []
            while i <= digits + 1:
                # The first digit is still the integer part, which we
                # can ignore!
                l.append(numerator // denominator)
                numerator = (numerator % denominator) * b
                if numerator == 0:
                    # Exact!
                    break
                i += 1
            # Check if we need to round.
            if len(l) > digits + 1:
                # Rounding seems not well-defined for odd-numbered
                # bases, but for now we don't have any of those.
                l[-2] += l[-1] // (int(math.ceil(b/2)))
                l.pop()
            lookup = cls._hex_lookup
            if len(l) == 1:
                return sign + conv(l[0])
            else:
                return (
                    sign + conv(l[0]) + "." + "".join(lookup[d] for d in l[1:])
                )

    # Pretty-printing ##################################################
    def as_string(self, mode=Mode.to_float,
                  numeral_system=NumeralSystem.decimal,
                  digits=_DEFAULT_DIGITS, units=UnitMode.none):
        """Pretty-printing for string output.

        ....

        Will prefix equals sign if deemed appropriate.

        """
        # TODO: THIS METHOD SUCKS, THE as_html() ONE IS BETTER!
        # TODO: probably some code is shared with the `n()' method above!
        # TODO: walk through expressions, so that we can apply the
        # following rules:
        #   * in try_exact mode, still apply "digits" precision to floats
        #   * when not outputting to decimal, we need to do it ourselves
        #   * we need to descend into expressions anyway!
        if isinstance(self.raw_result, bool):
            return "true" if self.raw_result else "false"
        # No, it's a more complicated expression.
        if mode == Mode.to_float:
            if isinstance(self.raw_result, Solutions):
                res = self.raw_result.apply(self._to_float, digits)
            else:
                res = self._to_float(self.raw_result, digits)
        elif mode == Mode.try_exact:
            if isinstance(self.raw_result, Solutions):
                res = self.raw_result.apply(self._simplify)
            else:
                res = self._simplify(self.raw_result)
        # Apply numeral system.
        # TODO: Here we would have to walk the expression.
        # TODO: apply to Solutions object, too! (also print those!)
        # TODO: apply to Quantity object, too!
        # TODO: support complex numbers
        # TODO: keep exact mode also here!!!
        if isinstance(res, sympy.Basic) and res.is_real:
            if numeral_system in (NumeralSystem.binary,
                                  NumeralSystem.octal,
                                  NumeralSystem.hexadecimal):
                res = "= " + self._to_other_base(res, numeral_system, digits)
            elif numeral_system == NumeralSystem.roman:
                res = "= " + RomanInt.int_to_roman(res)
            else:
                res = "= " + str(res)
        elif isinstance(res, Solutions):
            # TODO: recursive application of the previous actions :-(
            res = "\n".join("{} = {}".format(res.x, sol)
                            for sol in res.solutions)
        else:
            res = "= " + str(res)
        # TODO: unit thing.
        return res

    @classmethod
    def _decimal_as_html(cls, number, numeral_system, digits):
        # Special case some floats.
        if number == float("inf"):
            return "∞"
        elif number == float("-inf"):
            return "-∞"
        # "Normal" floats.
        if numeral_system == NumeralSystem.decimal:
            # Set precision.
            f = str(number.evalf(n=digits))
            # Fix ugliness.
            pre, exp = (f.split("e") + [""])[:2] # ensure length 2 :-(
            # Non-exponential part.
            pre1, pre2 = pre.split(".")
            #pre1 = pre1.lstrip("+0")  # won't happen, I think
            pre2 = pre2.rstrip("0")
            if pre2:
                pre = pre1 + "." + pre2
            else:
                pre = pre1
            # Exponential part.
            exp = exp.lstrip("+0")
            if not exp:
                return pre
            return pre + "·" + "10<sup>" + exp + "</sup>"
        elif numeral_system == NumeralSystem.roman:
            # This may raise a ValueError, if the float does not
            # correspond to an integer in the supported range.
            return RomanInt.int_to_roman(number)
        else:
            return cls._to_other_base(number, numeral_system, digits)

    @classmethod
    def _integer_as_html(cls, number, numeral_system, digits):
        if numeral_system == NumeralSystem.decimal:
            return str(number)
        elif numeral_system == NumeralSystem.roman:
            return RomanInt.int_to_roman(number)
        else:
            return cls._to_other_base(number, numeral_system, digits)

    @classmethod
    def _atom_as_html(cls, atom, mode, numeral_system, digits):
        if atom == sympy.I:
            # There is no float representation, return immediately.
            return "i"
        elif atom == sympy.zoo:
            return "z∞"
        elif atom == sympy.oo:
            return "∞"
        elif atom == -sympy.oo: # this is another type even
            return "-∞"
        elif isinstance(atom, sympy.numbers.NaN):
            return "NaN"
        # Exact or float?
        if mode == Mode.to_float:
            atom = atom.evalf(digits)
        elif mode == Mode.try_exact:
            atom = atom
        else:
            raise RuntimeError(
                "Mode is {}, but we can't handle it. This is a bug (wan35E)."
                "".format(mode)
            )
        if isinstance(atom, sympy.Float):
            return cls._decimal_as_html(atom, numeral_system, digits)
        elif atom == sympy.E:
            return "e" # would be upper case otherwise :-(
        elif atom == sympy.pi:
            return "π"
        else:
            return str(atom)

    @classmethod
    def _as_html(cls, raw_result, mode, numeral_system, digits, units):
        # Simplify result.
        if isinstance(raw_result, bool):
            # No need to simplify or do anything else, really.
            return "true" if raw_result else "false"
        elif isinstance(raw_result, Solutions):
            # Make a table out of solutions.
            return (
                '<table border="0" style="float:right;">'
                + "".join('<tr><td><i>{!s}</i> = </td><td>{}</td></tr>'
                          ''.format(raw_result.x,
                                    cls._as_html(i, mode, numeral_system,
                                                 digits, units))
                          for i in raw_result.solutions)
                + '</table>'
            )
        elif isinstance(raw_result, sympy.Equality):
            # Unsolved equality.
            return (
                cls._as_html(raw_result.lhs,
                             mode, numeral_system, digits, units)
                + " = "
                + cls._as_html(raw_result.rhs,
                               mode, numeral_system, digits, units)
            )
        elif isinstance(raw_result, (sympy.Rational, sympy.Float)):
            # Those need neither simplify() nor evalf() right now.
            result = raw_result
        else:
            if mode == Mode.to_float:
                result = raw_result.evalf(digits*10) # precision will be
                                                     # lowered later.
            elif mode == Mode.try_exact:
                # Try to simplify first.
                result = raw_result.simplify()
            else:
                raise RuntimeError(
                    "Mode is {}, but we can't handle it. "
                    "This is a bug (ea4djf)."
                    "".format(mode)
                )
        # Recurse through expression.
        def printer(expr, context):
            # TODO: big parentheses!
            if isinstance(expr, sympy.Symbol):
                return "<i>" + str(expr) + "</i>"
            elif isinstance(expr, unitbridge.Quantity):
                u = expr.unity_quantity
                m = expr.magnitude
                if units == UnitMode.none:
                    pass
                elif units == UnitMode.to_base:
                    u = u.to_base_units()
                    m = m * u.magnitude
                    u = Q_(1, u.units)
                elif units == UnitMode.to_best:
                    raise ValueError("'to best units' not implemented :-(")
                else:
                    raise RuntimeError("Unknown unit mode: {}. "
                                       "This is a bug (d6QtSj)."
                                       "".format(units))
                us = "{:~H}".format(u).lstrip("1").lstrip(" ")
                if us == "dimensionless":
                    return printer(m, context) # keeps context.
                elif (context.surrounding_op == cls._Surr.exp_base
                      or
                      (
                          context.surrounding_op == cls._Surr.exp_exp
                          and
                          context.is_exponent > 1
                      )):
                    ctxt = cls._Context(context.is_exponent,
                                        cls._Surr.multiplication)
                    return "(" + printer(m, ctxt) + " " + us + ")"
                else:
                    ctxt = cls._Context(context.is_exponent,
                                        cls._Surr.multiplication)
                    return printer(m, ctxt) + " " + us
            elif isinstance(expr, sympy.Float):
                retval = cls._decimal_as_html(expr, numeral_system, digits)
                if (context.surrounding_op == cls._Surr.exp_base
                    and expr < 0):
                    retval = "(" + retval + ")"
                return retval
            elif isinstance(expr, sympy.Integer):
                retval = cls._integer_as_html(expr, numeral_system, digits)
                if (context.surrounding_op == cls._Surr.exp_base
                    and expr < 0):
                    retval = "(" + retval + ")"
                return retval
            elif isinstance(expr, sympy.Rational):
                if mode == Mode.to_float:
                    return cls._decimal_as_html(expr, numeral_system, digits)
                elif expr == sympy.Rational(1,2):
                    return "½"
                elif expr == sympy.Rational(1,3):
                    return "⅓"
                elif expr == sympy.Rational(1,4):
                    return "¼"
                elif expr == sympy.Rational(1,5):
                    return "⅕"
                elif expr == sympy.Rational(1,6):
                    return "⅙"
                elif expr == sympy.Rational(1,7):
                    return "⅐"
                elif expr == sympy.Rational(1,8):
                    return "⅛"
                elif expr == sympy.Rational(1,9):
                    return "⅑"
                elif expr == sympy.Rational(1,10):
                    return "⅒"
                elif expr == sympy.Rational(1,10):
                    return "⅒"
                elif expr == sympy.Rational(2,3):
                    return "⅔"
                elif expr == sympy.Rational(3,4):
                    return "¾"
                elif expr == sympy.Rational(3,4):
                    return "¾"
                elif expr == sympy.Rational(2,5):
                    return "⅖"
                elif expr == sympy.Rational(3,5):
                    return "⅗"
                elif expr == sympy.Rational(4,5):
                    return "⅘"
                elif expr == sympy.Rational(5,6):
                    return "⅚"
                elif expr == sympy.Rational(3,8):
                    return "⅜"
                elif expr == sympy.Rational(5,8):
                    return "⅝"
                elif expr == sympy.Rational(7,8):
                    return "⅞"
                elif context.is_exponent:
                    if (context.surrounding_op == cls._Surr.exp_base
                        or
                        (context.surrounding_op == cls._Surr.exp_exp
                         and
                         context.is_exponent > 1
                         )):
                        pre = "("
                        post = ")"
                    else:
                        pre = ""
                        post = ""
                    mid = "/"
                elif context.surrounding_op == cls._Surr.exp_base:
                    # TODO: fraction sucks in HTML :-(
                    pre = "(<sup>"
                    mid = "</sup>&frasl;<sub>"
                    post = "</sub>)"
                else:
                    # TODO: fraction sucks in HTML :-(
                    pre = "<sup>"
                    mid = "</sup>&frasl;<sub>"
                    post = "</sub>"
                return (
                    pre
                    + cls._integer_as_html(expr.p, numeral_system, digits)
                    + mid
                    + cls._integer_as_html(expr.q, numeral_system, digits)
                    + post
                )
            elif isinstance(expr, sympy.Atom):
                return cls._atom_as_html(expr, mode, numeral_system, digits)
            elif isinstance(expr, sympy.Add):
                ctxt = cls._Context(context.is_exponent,
                                    cls._Surr.addition)
                if (context.surrounding_op in {cls._Surr.multiplication,
                                               cls._Surr.exp_base}
                    or
                    (context.surrounding_op == cls._Surr.exp_exp
                     and
                     context.is_exponent > 1)):
                    return "(" + " + ".join(printer(summand, ctxt)
                                            for summand in expr.args) + ")"
                else:
                    return " + ".join(printer(summand, ctxt)
                                      for summand in expr.args)
            elif isinstance(expr, sympy.Mul):
                # TODO: fraction (investigate nested Pow)!
                # TODO: leave out multiplication sign before constant!
                args = [factor for factor in expr.args if factor != 1]
                if not args:
                    return "1"
                elif len(args) == 1:
                    return printer(args[0], context)
                elif len(args) == 2 and args[0] == -1:
                    # TODO: hopefully the second arg never has a minus
                    # sign itself!?
                    if context.surrounding_op == cls._Surr.exp_base:
                        return "(-" + printer(args[1], context) +")"
                    else:
                        return "-" + printer(args[1], context)
                elif (context.surrounding_op == cls._Surr.exp_base
                      or
                      (context.surrounding_op == cls._Surr.exp_exp
                       and
                       context.is_exponent > 1)):
                    ctxt = cls._Context(context.is_exponent,
                                        cls._Surr.multiplication)
                    return "(" + " · ".join(printer(factor, ctxt)
                                            for factor in args) + ")"
                else:
                    ctxt = cls._Context(context.is_exponent,
                                        cls._Surr.multiplication)
                    return " · ".join(printer(factor, ctxt)
                                      for factor in args)
            elif isinstance(expr, sympy.Pow):
                # TODO: multiple exponents suck in HTML
                # TODO: needs parentheses sometimes!!!!!!!!!!      
                #    e.g. (x^x)^x^(x^x)^x
                ctxt_base = cls._Context(context.is_exponent,
                                         cls._Surr.exp_base)
                ctxt_exp = cls._Context(context.is_exponent+1,
                                        cls._Surr.exp_exp)
                if context.is_exponent:
                    retval = (
                        printer(expr.args[0], ctxt_base)
                        + "^"
                        + printer(expr.args[1], ctxt_exp)
                    )
                else:
                    retval = (
                        printer(expr.args[0], ctxt_base)
                        + "<sup>" + printer(expr.args[1], ctxt_exp) + "</sup>"
                    )
                if context.surrounding_op == cls._Surr.exp_base:
                    return "(" + retval + ")"
                else:
                    return retval
            elif isinstance(expr, sympy.Function):
                # TODO: sympy.Function -> look up name in a table, the
                # same table we use to map from string to
                # function. This table needs to be made, of course,
                # but it should contain also the help strings.
                ctxt = cls._Context(context.is_exponent,
                                    cls._Surr.function_call)
                return (
                    str(expr.func) + "("
                    + ", ".join(printer(arg, ctxt) for arg in expr.args)
                    + ")"
                )
            elif isinstance(expr, sympy.ImmutableMatrix):
                # TODO: make a table (special case vector to always be
                # a column?)
                if expr.shape == (1,1):
                    # Treat 1x1 matrix as scalar.
                    return printer(expr[0], context)
                ctxt = cls._Context(context.is_exponent,
                                    cls._Surr.none)
                # Special case 1-row matrix to vector.
                if expr.shape[0] == 1:
                    expr = expr.transpose()
                last = expr.rows - 1
                # TODO: using float:right always a good idea?
                retval = (
                    '<table border="0" cellspacing="0" style="float:right;">'
                )
                for i in range(expr.rows):
                    row = expr.row(i)
                    retval += "<tr><td>"
                    if expr.rows == 1:
                        retval += "["
                    elif i == 0:
                        retval += "⎡"
                    elif i == last:
                        retval += "⎣"
                    else:
                        retval += "⎢"
                    rowlast = len(row) - 1
                    for j, item in enumerate(row):
                        retval += (('<td style="padding-right:15px;">'
                                    if j < rowlast
                                    else "<td>")
                                   + printer(item, ctxt)
                                   + "</td>")
                    retval += "<td>"
                    if expr.rows == 1:
                        retval += "]"
                    elif i == 0:
                        retval += "⎤"
                    elif i == last:
                        retval += "⎦"
                    else:
                        retval += "⎥"
                    retval += "</td></tr>"
                retval += "</table>"
                return retval
            elif isinstance(expr, sympy.RootOf):
                # No symbolic solution available.
                return printer(expr.evalf(2*digits), # reduce digits later.
                               context)
            else:
                raise RuntimeError(
                    "Unsupported type for printing: {}. Bug 3a89Bj."
                    "".format(type(expr))
                )
        return printer(result, cls._Context(0, cls._Surr.none))

    def as_html(self, mode=Mode.to_float,
                numeral_system=NumeralSystem.decimal,
                digits=_DEFAULT_DIGITS, units=UnitMode.none):
        return self._as_html(self.raw_result, mode, numeral_system,
                             digits, units)


class Solutions:
    """A list of solutions."""

    def __init__(self, x, solutions):
        self.x = x
        self.solutions = tuple(solutions)

    def apply(self, fn, *args, **kwargs):
        """Apply function fn(<>, *args, **kwargs) to every solution.

        Returns a new Solutions object.

        """
        return self.__class__(self.x, tuple(fn(sol, *args, **kwargs)
                                            for sol in self.solutions))
