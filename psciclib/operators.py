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


class Wrapper:
    """This is the primary API for complete command lines.

    It is a thin wrapper around Expression, Conversion, etc.

    """
    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        return str(self.cmd)

    def evaluate_exact(self, **kwargs):
        """Evaluate, not converting explicitly to float."""
        return self.cmd.evaluate(**kwargs)

    def evaluate(self, **kwargs):
        """Evaluate human-readable.

        That means, convert to float where not already float or integer.

        """
        evaluated = self.evaluate_exact(**kwargs)
        # Strip unit.
        if isinstance(evaluated, units.Q_):
            magnitude = evaluated.magnitude
        else:
            magnitude = evaluated
        # Eval to float if necessary.
        if (not isinstance(magnitude, sympy.numbers.Integer)
            and not isinstance(magnitude, sympy.numbers.Float)):
            magnitude = magnitude.evalf()
        # Add unit if necessary and return.
        if isinstance(evaluated, units.Q_):
            return units.Q_(magnitude, evaluated.units)
        else:
            return magnitude


# Helper classes for primitive literals.
def process_int(s, loc, toks):
    return sympy.Integer(toks[0])


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

    _D = collections.namedtuple("_D", ["canonical_name", "fn"])

    _functions = {
        # Trigonometric functions.
        "sin": _D("sin", sympy.sin),
        "cos": _D("cos", sympy.cos),
        "tan": _D("tan", sympy.tan),
        "cot": _D("cot", sympy.cot),
        "sec": _D("sec", sympy.sec),
        "csc": _D("cosec", sympy.csc),
        "cosec": _D("cosec", sympy.csc),
        # Inverse trigonometric functions.
        "asin": _D("arcsin", sympy.asin),
        "arcsin": _D("arcsin", sympy.asin),
        "acos": _D("arccos", sympy.acos),
        "arccos": _D("arccos", sympy.acos),
        "atan": _D("arctan", sympy.atan),
        "arctan": _D("arctan", sympy.atan),
        "acot": _D("arccot", sympy.acot),
        "arccot": _D("arccot", sympy.acot),
        "asec": _D("arcsec", sympy.asec),
        "arcsec": _D("arcsec", sympy.asec),
        "acsc": _D("arccosec", sympy.acsc),
        "arccsc": _D("arccosec", sympy.acsc),
        "acosec": _D("arccosec", sympy.acsc),
        "arccosec": _D("arccosec", sympy.acsc),
        # Hyperbolic functions.
        "sinh": _D("sinh", sympy.sinh),
        "cosh": _D("cosh", sympy.cosh),
        "tanh": _D("tanh", sympy.tanh),
        "coth": _D("coth", sympy.coth),
        "sech": _D("sech", lambda x: 1/sympy.cosh(x)),
        "csch": _D("cosech", lambda x: 1/sympy.sinh(x)),
        "cosech": _D("cosech", lambda x: 1/sympy.sinh(x)),
        # Inverse hyperbolic functions.
        "asinh": _D("arsinh", sympy.asinh),
        "arsinh": _D("arsinh", sympy.asinh),
        "acosh": _D("arcosh", sympy.acosh),
        "arcosh": _D("arcosh", sympy.acosh),
        "atanh": _D("artanh", sympy.atanh),
        "artanh": _D("artanh", sympy.atanh),
        "acoth": _D("arcoth", sympy.acoth),
        "arcoth": _D("arcoth", sympy.acoth),
        "asech": _D("arsech", lambda x: sympy.acosh(1/x)),
        "arsech": _D("arsech", lambda x: sympy.acosh(1/x)),
        "acsch": _D("arcosech", lambda x: sympy.asinh(1/x)),
        "arcsch": _D("arcosech", lambda x: sympy.asinh(1/x)),
        "acosech": _D("arcosech", lambda x: sympy.asinh(1/x)),
        "arcosech": _D("arcosech", lambda x: sympy.asinh(1/x)),
        # e-function related.
        "exp": _D("exp", sympy.exp),
        "ln": _D("log", sympy.log),
        "log": _D("log", sympy.log),
        "log10": _D("log10", lambda x: sympy.log(x, 10)),
        "log2": _D("log2", lambda x: sympy.log(x, 2)),
        # Square root.
        "sqrt": _D("√", sympy.sqrt),
        "√": _D("√", sympy.sqrt),
        # Absolute.
        "abs": _D("abs", abs),
        # Error function.
        "erf": _D("erf", sympy.erf),
        "erfc": _D("erfc", sympy.erfc),
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
        "x": _D("x", sympy.symbols("x")),
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

