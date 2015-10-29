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

import abc
import collections

from pyparsing import ParseResults
import sympy

from .exceptions import (UnknownFunctionError,
                         UnknownConstantError,
                         UnknownUnitError)
from . import units


_X = sympy.Symbol("x")


def _apply(obj, method, args, kwargs, exclude_classes=()):
    """Call method on obj, except if obj is instance of on of exclude_classes.

    If the object is a pint Quantity, only call the method on the
    magnitude, not the unit. Method is called with args and kwargs.

    """
    if isinstance(obj, exclude_classes):
        return obj
    # Strip unit.
    is_q = isinstance(obj, units.Q_)
    if is_q:
        magnitude = obj.magnitude
    else:
        magnitude = obj
    magnitude = getattr(magnitude, method)(*args, **kwargs)
    if is_q:
        return units.Q_(magnitude, obj.units)
    else:
        return magnitude


class Wrapper:
    """This is the primary API for complete command lines.

    It is a thin wrapper around Expression, Conversion, etc.

    """
    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        return str(self.cmd)

    def evaluate_asis(self, **kwargs):
        """Evaluate, not converting explicitly to float."""
        return self.cmd.evaluate(**kwargs)

    def evaluate(self, **kwargs):
        """Evaluate human-readable.

        That means, convert to float where not already float or integer.

        """
        evaluated = self.evaluate_asis(**kwargs)
        return _apply(evaluated, "evalf", (), {},
                      exclude_classes=(sympy.numbers.Integer,
                                       sympy.numbers.Float,
                                       bool))

    def evaluate_simplify(self, **kwargs):
        """Evaluate, not converting to float, but trying to simplify
        expression."""
        evaluated = self.evaluate_asis(**kwargs)
        return _apply(evaluated, "simplify", (), {},
                      exclude_classes=(bool,))


# Helper classes for primitive literals.
def process_int(s, loc, toks):
    return sympy.Integer(toks[0])


__bases = {"0x": 16, "0o": 8, "0b": 2}
def process_intbase(s, loc, toks):
    base = __bases[toks[0][0]]
    i = int(toks[0][1], base)
    return sympy.Integer(i)


def process_realbase(s, loc, toks):
    int_part = toks[0][0]
    base = __bases[toks[0][0]]
    i = sympy.Integer(int(toks[0][1], base))
    frac_part = toks[0][3]
    exp = len(frac_part)
    r = sympy.Rational(int(frac_part, base), base**exp)
    return i+r


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
    def process(cls, s, loc, toks):
        _, thousands, hundreds, tens, ones = toks[0]
        i = len(thousands) * 1000
        i += cls.table[hundreds] + cls.table[tens] + cls.table[ones]
        return sympy.Integer(i)

    @classmethod
    def int_to_roman(cls, integer):
        # TODO: test this method!!!!    
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


def process_float(s, loc, toks):
    return sympy.Float(toks[0])


class Operator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def evaluate(self, **kwargs):
        # The kwargs give values to variables!
        # TODO: the above is stupid, use sympy's subs() method at the end!!!   
        #
        #TODO for all subclasses: handle symbolic variable by not     
        #actually evaluating!                                         
        #
        #TODO: also try to simplify expressions with variables in it  
        pass

    @classmethod
    @abc.abstractmethod
    def process(cls, s, loc, toks):
        # Process parse results.  Implementations should return a
        # ParseResults object.
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    @staticmethod
    def _eval(*args, **kwargs):
        """For every arg, return the evaluated form.

        If an arg is an instance of Operator call .evaluate(),
        otherwise pass it back as is.

        Any keyword arg is interpreted as assigning a value to a variable.

        """
        return tuple((arg.evaluate(**kwargs)
                      if isinstance(arg, Operator)
                      else arg)
                     for arg in args)


class Expression(Operator):
    """A whole expression (i.e., no equal sign etc., just a term)."""
    def __init__(self, expr):
        self.expr = expr

    @classmethod
    def process(cls, s, loc, toks):
        if len(toks) != 1:
            raise ValueError("BUG: Something went wrong with the parsing.")
        return cls(toks[0])

    def __str__(self):
        return str(self.expr)

    def evaluate(self, **kwargs):
        """Evaluate the expression."""
        retval, = self._eval(self.expr, **kwargs)
        return retval


class Conversion(Operator):
    """<expression> to <unit>"""
    def __init__(self, expr, to_unit):
        self.expr = expr
        self.to_unit = to_unit

    @classmethod
    def process(cls, s, loc, toks):
        if len(toks) != 3:
            raise ValueError("BUG: Something went wrong with the parsing.")
        # [<expr>, "to", <unit_expr>]
        return cls(toks[0], toks[2])

    def __str__(self):
        return "{!s} to {!s}".format(self.expr, self.to_unit)

    def evaluate(self, **kwargs):
        """Evaluate the expression and convert to requested unit."""
        expr, to_unit = self._eval(self.expr, self.to_unit, **kwargs)
        if not isinstance(expr, units.Q_):
            expr = units.Q_(expr) # dimensionless
        return expr.to(to_unit)


class Equality(Operator):
    """<lhs> = <rhs>, autosolved if possible."""

    class Solutions:
        # Helper class for pretty-printing.
        def __init__(self, x, solutions):
            self.x = x
            self.solutions = solutions

        def __str__(self):
            if len(self.solutions) == 1:
                return "{} = {}".format(self.x, self.solutions[0])
            else:
                return "{} = [{}]".format(self.x,
                                          "; ".join(str(i)
                                                   for i in self.solutions))

        def evalf(self, *args, **kwargs):
            return self.__class__(self.x, [_apply(i, "evalf", args, kwargs)
                                           for i in self.solutions])

        def simplify(self, *args, **kwargs):
            return self.__class__(self.x, [_apply(i, "simplify", args, kwargs)
                                           for i in self.solutions])

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    @classmethod
    def process(cls, s, loc, toks):
        if len(toks) != 3:
            raise ValueError("BUG: Something went wrong with the parsing.")
        # [<lhs>, "=", <rhs>]
        return cls(toks[0], toks[2])

    def __str__(self):
        return "{!s} = {!s}".format(self.lhs, self.rhs)

    def evaluate(self, **kwargs):
        """Try to solve."""
        lhs, rhs = self._eval(self.lhs, self.rhs, **kwargs)
        true, false = sympy.S.true, sympy.S.false
        eq = sympy.Eq(lhs, rhs)
        # Check if we can already say the expression is true or false.
        if eq is true or eq is false:
            return bool(eq)
        # Try harder.
        eq = eq.simplify()
        if eq is true or eq is false:
            return bool(eq)
        # Try to solve for x.
        try:
            solutions = sympy.solve(eq, _X)
        except NotImplementedError:
            solutions = []
        if not solutions:
            return eq
        else:
            return self.Solutions(_X, solutions)


class SymbolOperator(Operator):
    pass


class InfixSymbol(SymbolOperator):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "({!s} {} {!s})".format(self.lhs, self.symbol, self.rhs)


class InfixLeftSymbol(InfixSymbol):
    @classmethod
    def process(cls, s, loc, toks):
        # Sadly, those cannot be stored in the class, as the
        # subclasses are not yet defined. In the interest of
        # simplicity just keep them here as a local variable.
        symbols = {
            "+": Plus,
            "-": Minus,
            "*": Times,
            "·": Times,
            "/": Divide,
            "÷": Divide,
            "//": IntDivide,
        }
        symb_set = set(symbols.keys())
        # reverse, as append is faster than insert(0)
        l = list(reversed(toks[0]))
        while len(l) > 1:
            lhs = l.pop()
            op = l.pop()
            # Check if operator was omitted (i.e. a multiplication
            # without sign)
            if op in symb_set:
                rhs = l.pop()
            else:
                # multiplication operator was omitted.
                rhs = op
                op = "*"
            # We will never get, e.g., +- mixed with */ due to the
            # parsing. Therefore it is fine to mix them wildly here
            # without error checking.
            try:
                cls_ = symbols[op]
            except KeyError:
                raise ValueError("Unknown infix operator: {}".format(op))
            l.append(cls_(lhs, rhs))
        return ParseResults(l)


class Plus(InfixLeftSymbol):
    symbol = "+"

    def evaluate(self, **kwargs):
        lhs, rhs = self._eval(self.lhs, self.rhs, **kwargs)
        return lhs + rhs


class Minus(InfixLeftSymbol):
    symbol = "-"

    def evaluate(self, **kwargs):
        lhs, rhs = self._eval(self.lhs, self.rhs, **kwargs)
        return lhs - rhs


class Times(InfixLeftSymbol):
    symbol = "·"

    def evaluate(self, **kwargs):
        lhs, rhs = self._eval(self.lhs, self.rhs, **kwargs)
        return lhs * rhs


class Divide(InfixLeftSymbol):
    symbol = "÷"

    def evaluate(self, **kwargs):
        lhs, rhs = self._eval(self.lhs, self.rhs, **kwargs)
        return lhs / rhs


class IntDivide(InfixLeftSymbol):
    symbol = "//"

    def evaluate(self, **kwargs):
        lhs, rhs = self._eval(self.lhs, self.rhs, **kwargs)
        return sympy.floor(lhs / rhs)


class Exponent(InfixSymbol):
    symbol = "^"

    @classmethod
    def process(cls, s, loc, toks):
        lhs = toks[0][0]
        # Find signs in exponent.
        signs = []
        while toks[0][2] in ("+", "-"):
            signs.append(toks[0].pop(2))
        if signs:
            signs.append(toks[0].pop())
            while len(signs) > 1:
                b = signs.pop()
                a = signs.pop()
                signs.append(PrefixSymbol.process(None, None,
                                                  [ParseResults([a, b])])[0])
            rhs = signs[0]
        else:
            rhs = toks[0][2]
        return cls(lhs, rhs)

    def evaluate(self, **kwargs):
        lhs, rhs = self._eval(self.lhs, self.rhs, **kwargs)
        # Exponentiation of units does not play nice with pint/sympy,
        # so fix that.
        # TODO: the exponent could be a sympy symbol, that is not yet
        # supported     
        if isinstance(lhs, units.Q_):
            # Try to make rhs into a float.
            try:
                unit_exponent = float(rhs)
            except TypeError:
                raise ValueError("Exponents for units must be real numbers, "
                                 "not {}.".format(type(rhs)))
            m = lhs.magnitude
            u = lhs.units
            return units.Q_(m ** rhs, u ** unit_exponent)
        else:
            return lhs ** rhs


class PostfixSymbol(SymbolOperator):
    def __init__(self, lhs):
        self.lhs = lhs

    def __str__(self):
        return "({!s}{})".format(self.lhs, self.symbol)

    @classmethod
    def process(cls, s, loc, toks):
        l = list(reversed(toks[0]))# reverse, as append is faster than insert(0)
        while len(l) > 1:
            lhs = l.pop()
            op = l.pop()
            if op == "!":
                l.append(Factorial(lhs))
            else:
                raise ValueError("Unknown postfix operator: {}".format(op))
        return ParseResults(l)


class Factorial(PostfixSymbol):
    symbol = "!"

    def evaluate(self, **kwargs):
        lhs, = self._eval(self.lhs, **kwargs)
        return sympy.factorial(lhs)


class PrefixSymbol(SymbolOperator):
    def __init__(self, rhs):
        self.rhs = rhs

    def __str__(self):
        return "({}{!s})".format(self.symbol, self.rhs)

    @classmethod
    def process(cls, s, loc, toks):
        op, rhs = toks[0]
        if op == "+":
            obj = PlusSign(rhs)
        elif op == "-":
            obj = MinusSign(rhs)
        else:
            raise ValueError("Unknown prefix operator: {}".format(sign))
        return ParseResults([obj])


class MinusSign(PrefixSymbol):
    symbol = "-"

    def evaluate(self, **kwargs):
        rhs, = self._eval(self.rhs, **kwargs)
        return -rhs


class PlusSign(PrefixSymbol):
    symbol = "+"

    def evaluate(self, **kwargs):
        rhs, = self._eval(self.rhs, **kwargs)
        return rhs

class Function(Operator):

    # If the function can handle units other than dimensionless,
    # unit_support should be a function to be applied to the unit,
    # otherwise False.  If the function already handles units, use True.
    _D = collections.namedtuple("_D", ["canonical_name", "fn", "unit_support"])

    _functions = {
        # Trigonometric functions.
        "sin": _D("sin", sympy.sin, False),
        "cos": _D("cos", sympy.cos, False),
        "tan": _D("tan", sympy.tan, False),
        "cot": _D("cot", sympy.cot, False),
        "sec": _D("sec", sympy.sec, False),
        "csc": _D("cosec", sympy.csc, False),
        "cosec": _D("cosec", sympy.csc, False),
        # Inverse trigonometric functions.
        "asin": _D("arcsin", sympy.asin, False),
        "arcsin": _D("arcsin", sympy.asin, False),
        "acos": _D("arccos", sympy.acos, False),
        "arccos": _D("arccos", sympy.acos, False),
        "atan": _D("arctan", sympy.atan, False),
        "arctan": _D("arctan", sympy.atan, False),
        "acot": _D("arccot", sympy.acot, False),
        "arccot": _D("arccot", sympy.acot, False),
        "asec": _D("arcsec", sympy.asec, False),
        "arcsec": _D("arcsec", sympy.asec, False),
        "acsc": _D("arccosec", sympy.acsc, False),
        "arccsc": _D("arccosec", sympy.acsc, False),
        "acosec": _D("arccosec", sympy.acsc, False),
        "arccosec": _D("arccosec", sympy.acsc, False),
        # Hyperbolic functions.
        "sinh": _D("sinh", sympy.sinh, False),
        "cosh": _D("cosh", sympy.cosh, False),
        "tanh": _D("tanh", sympy.tanh, False),
        "coth": _D("coth", sympy.coth, False),
        "sech": _D("sech", lambda x: 1/sympy.cosh(x), False),
        "csch": _D("cosech", lambda x: 1/sympy.sinh(x), False),
        "cosech": _D("cosech", lambda x: 1/sympy.sinh(x), False),
        # Inverse hyperbolic functions.
        "asinh": _D("arsinh", sympy.asinh, False),
        "arsinh": _D("arsinh", sympy.asinh, False),
        "acosh": _D("arcosh", sympy.acosh, False),
        "arcosh": _D("arcosh", sympy.acosh, False),
        "atanh": _D("artanh", sympy.atanh, False),
        "artanh": _D("artanh", sympy.atanh, False),
        "acoth": _D("arcoth", sympy.acoth, False),
        "arcoth": _D("arcoth", sympy.acoth, False),
        "asech": _D("arsech", lambda x: sympy.acosh(1/x), False),
        "arsech": _D("arsech", lambda x: sympy.acosh(1/x), False),
        "acsch": _D("arcosech", lambda x: sympy.asinh(1/x), False),
        "arcsch": _D("arcosech", lambda x: sympy.asinh(1/x), False),
        "acosech": _D("arcosech", lambda x: sympy.asinh(1/x), False),
        "arcosech": _D("arcosech", lambda x: sympy.asinh(1/x), False),
        # e-function related.
        "exp": _D("exp", sympy.exp, False),
        "ln": _D("log", sympy.log, False),
        "log": _D("log", sympy.log, False),
        "log10": _D("log10", lambda x: sympy.log(x, 10), False),
        "log2": _D("log2", lambda x: sympy.log(x, 2), False),
        # Square root.
        "sqrt": _D("√", sympy.sqrt, lambda u: u**0.5),
        "√": _D("√", sympy.sqrt, lambda u: u**0.5),
        # Error function.
        "erf": _D("erf", sympy.erf, False),
        "erfc": _D("erfc", sympy.erfc, False),
        # Misc.
        "abs": _D("abs", abs, True),
        "floor": _D("floor", sympy.floor, False),
        "ceil": _D("ceil", sympy.ceiling, False),
        # Geometry.
        "circle_area": _D("circle_area", lambda r: sympy.pi * r**2, True),
        "circle_circ": _D("circle_circumference",
                          lambda r: 2 * sympy.pi * r, True),
        "circle_circumference": _D("circle_circumference",
                                   lambda r: 2 * sympy.pi * r, True),
        "sphere_vol": _D("sphere_volume",
                         lambda r: sympy.Rational(4,3) * sympy.pi * r**3,
                         True),
        "sphere_volume": _D("sphere_volume",
                            lambda r: sympy.Rational(4,3) * sympy.pi * r**3,
                            True),
        "sphere_surf": _D("sphere_surface",
                          lambda r: 4 * sympy.pi * r**2,
                          True),
        "sphere_surface": _D("sphere_surface",
                             lambda r: 4 * sympy.pi * r**2,
                             True),
    }

    @classmethod
    def process(cls, s, loc, toks):
        # TODO: multiple arguments
        try:
            fn_s, fn, unit_support = cls._functions[toks[0][0]]
        except KeyError:
            raise UnknownFunctionError(toks[0][0])
        arg = toks[0][1]
        return ParseResults([cls(fn_s, fn, arg, unit_support)])

    def __init__(self, fn_s, fn, arg, unit_support):
        # TODO: multiple arguments
        self.fn_s = fn_s
        self.fn = fn
        self.arg = arg
        self.unit_support = unit_support

    def __str__(self):
        return "{}({!s})".format(self.fn_s, self.arg)

    def evaluate(self, **kwargs):
        arg, = self._eval(self.arg, **kwargs)
        if self.unit_support is True or not isinstance(arg, units.Q_):
            return self.fn(arg)
        elif self.unit_support is False:
            return self.fn(arg.to("dimensionless"))
        else:
            m = arg.magnitude
            u = arg.units
            return units.Q_(self.fn(m), self.unit_support(u))


class Constant(Operator):
    # Constants and variables (which are nothing but constants here in
    # terms of implementation).

    _D = collections.namedtuple("_D", ["canonical_name", "value"])

    _constants_and_variables = {
        "e": _D("e", sympy.E),
        "i": _D("i", sympy.I),
        "pi": _D("π", sympy.pi),
        "π": _D("π", sympy.pi),

        # Variables.
        "x": _D("x", _X),
    }

    @classmethod
    def process(cls, s, loc, toks):
        try:
            name, value = cls._constants_and_variables[toks[0]]
        except KeyError:
            # Perhaps it is a unit known by pint?
            try:
                return Unit.process(s, loc, toks)
            except UnknownUnitError:
                raise UnknownConstantError(toks[0])
        return cls(name, value)

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return str(self.name)

    def evaluate(self, **kwargs):
        return self.value


class Unit(Constant):
    # A special kind of constant.

    @classmethod
    def process(cls, s, loc, toks):
        try:
            value = units.ureg(toks[0])
        except units.UndefinedUnitError:
            raise UnknownUnitError(toks[0])
        name = "{:~}".format(value) # includes a leading 1 :-(
        return cls(name, value)

