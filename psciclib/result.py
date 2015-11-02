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

# TODO: pretty-printing code could go here?

import enum
import math

import sympy

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
        # TODO: test this method!!!!    
        if not integer.is_integer:
            raise ValueError("Roman numerals are only supported for integers.")
        if integer < 1 or integer > 4999:
            raise ValueError("Roman numerals are only supported on the "
                             "interval [1;4999]!")
        retval = "M" * (integer // 1000)
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

    #TODO: MathML/Latex/... output and a widget that can handle it!


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
