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
import math
import collections

from pyparsing import ParseResults

from .exceptions import (UnknownFunctionError,
                         UnknownConstantError,
                         UnknownUnitError)
from . import units


class Operator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def evaluate(self, **kwargs):
        # The kwargs give values to variables!
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
        return tuple((arg.evaluate(**kwargs) if isinstance(arg, Operator) else arg)
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
        expr, to_unit = self._eval(self.expr, self.to_unit, **kwargs)
        if not isinstance(expr, units.Q_):
            expr *= units.ureg("1") # dimensionless
        return expr.to(to_unit)


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
        # reverse, as append is faster than insert(0)
        l = list(reversed(toks[0]))
        while len(l) > 1:
            lhs = l.pop()
            op = l.pop()
            rhs = l.pop()
            # We will never get, e.g., +- mixed with */ due to the
            # parsing. Therefore it is fine to mix them wildly here
            # without error checking.
            if op == "+":
                cls_ = Plus
            elif op == "-":
                cls_ = Minus
            elif op == "*" or op == "·":
                cls_ = Times
            elif op == "/" or op == "÷":
                cls_ = Divide
            elif op == "//":
                cls_ = IntDivide
            else:
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
        return int(lhs // rhs)


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
        return math.factorial(lhs)


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

    _D = collections.namedtuple("_D", ["canonical_name", "fn"])

    _functions = {
        # Trigonometric functions.
        "sin": _D("sin", math.sin),
        "cos": _D("cos", math.cos),
        "tan": _D("tan", math.tan),
        "cot": _D("cot", lambda x: 1/math.tan(x)),
        "sec": _D("sec", lambda x: 1/math.cos(x)),
        "csc": _D("cosec", lambda x: 1/math.sin(x)),
        "cosec": _D("cosec", lambda x: 1/math.sin(x)),
        # Inverse trigonometric functions.
        "asin": _D("arcsin", math.asin),
        "arcsin": _D("arcsin", math.asin),
        "acos": _D("arccos", math.acos),
        "arccos": _D("arccos", math.acos),
        "atan": _D("arctan", math.atan),
        "arctan": _D("arctan", math.atan),
        "acot": _D("arccot", lambda x: math.pi/2 - math.atan(x)),
        "arccot": _D("arccot", lambda x: math.pi/2 - math.atan(x)),
        "asec": _D("arcsec", lambda x: math.acos(1/x)),
        "arcsec": _D("arcsec", lambda x: math.acos(1/x)),
        "acsc": _D("arccosec", lambda x: math.asin(1/x)),
        "arccsc": _D("arccosec", lambda x: math.asin(1/x)),
        "acosec": _D("arccosec", lambda x: math.asin(1/x)),
        "arccosec": _D("arccosec", lambda x: math.asin(1/x)),
        # Hyperbolic functions.
        "sinh": _D("sinh", math.sinh),
        "cosh": _D("cosh", math.cosh),
        "tanh": _D("tanh", math.tanh),
        "coth": _D("coth", lambda x: math.cosh(x)/math.sinh(x)),
        "sech": _D("sech", lambda x: 1/math.cosh(x)),
        "csch": _D("cosech", lambda x: 1/math.sinh(x)),
        "cosech": _D("cosech", lambda x: 1/math.sinh(x)),
        # Inverse hyperbolic functions.
        "asinh": _D("arsinh", math.asinh),
        "arsinh": _D("arsinh", math.asinh),
        "acosh": _D("arcosh", math.acosh),
        "arcosh": _D("arcosh", math.acosh),
        "atanh": _D("artanh", math.atanh),
        "artanh": _D("artanh", math.atanh),
        "acoth": _D("arcoth", lambda x: math.atanh(1/x)),
        "arcoth": _D("arcoth", lambda x: math.atanh(1/x)),
        "asech": _D("arsech", lambda x: math.acosh(1/x)),
        "arsech": _D("arsech", lambda x: math.acosh(1/x)),
        "acsch": _D("arcosech", lambda x: math.asinh(1/x)),
        "arcsch": _D("arcosech", lambda x: math.asinh(1/x)),
        "acosech": _D("arcosech", lambda x: math.asinh(1/x)),
        "arcosech": _D("arcosech", lambda x: math.asinh(1/x)),
        # e-function related.
        "exp": _D("exp", math.exp),
        "ln": _D("log", math.log),
        "log": _D("log", math.log),
        "log10": _D("log10", math.log10),
        "log2": _D("log2", math.log2),
        # Square root.
        "sqrt": _D("√", math.sqrt),
        "√": _D("√", math.sqrt),
        # Absolute.
        "abs": _D("abs", abs),
        # Error function.
        "erf": _D("erf", math.erf),
        "erfc": _D("erfc", math.erfc),
    }

    @classmethod
    def process(cls, s, loc, toks):
        # TODO: multiple arguments
        try:
            fn_s, fn = cls._functions[toks[0][0]]
        except KeyError:
            raise UnknownFunctionError(toks[0][0])
        arg = toks[0][1]
        return ParseResults([cls(fn_s, fn, arg)])

    def __init__(self, fn_s, fn, arg):
        # TODO: multiple arguments
        self.fn_s = fn_s
        self.fn = fn
        self.arg = arg

    def __str__(self):
        return "{}({!s})".format(self.fn_s, self.arg)

    def evaluate(self, **kwargs):
        arg, = self._eval(self.arg, **kwargs)
        return self.fn(arg)


class ConstVar(Operator):
    # Base class for constants and variables.

    _D = collections.namedtuple("_D", ["canonical_name", "constvar", "value"])

    _constants_and_variables = {
        "e": _D("e", "const", math.e),
        "i": _D("i", "const", 1j),
        "pi": _D("π", "const", math.pi),
        "π": _D("π", "const", math.pi),

        # Variables.
        "x": _D("x", "var", None),
    }

    @classmethod
    def process(cls, s, loc, toks):
        try:
            name, type_, value = cls._constants_and_variables[toks[0]]
        except KeyError:
            # Perhaps it is a unit known by pint?
            try:
                return Unit.process(s, loc, toks)
            except UnknownUnitError:
                raise UnknownConstantError(toks[0])
        if type_ == "const":
            return ParseResults([Constant(name, value)])
        elif type_ == "var":
            return ParseResults([Variable(name)])

    def __str__(self):
        return str(self.name)


class Constant(ConstVar):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def evaluate(self, **kwargs):
        return self.value


class Variable(ConstVar):
    def __init__(self, name):
        self.name = name

    def evaluate(self, **kwargs):
        if self.name in kwargs:
            # This variable was assigned a value!
            return kwargs[self.name]
        else:
            # No, still symbolic.
            return self


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

