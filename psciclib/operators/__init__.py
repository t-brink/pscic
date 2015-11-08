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
import pint

from ..exceptions import (UnknownFunctionError,
                          UnknownConstantError,
                          UnknownUnitError,
                          WrongNumberOfArgumentsError,
                          VariableLengthRowsError)
from .. import units
from .. import unitbridge
from ..result import RomanInt, Result, Solutions
from .functions import FunctionList


_X = sympy.Symbol("x")


class Wrapper:
    """This is the primary API for complete command lines.

    It is a thin wrapper around Expression, Conversion, etc.

    """
    def __init__(self, input_str, cmd):
        self.input_str = input_str
        self.cmd = cmd

    def __str__(self):
        return str(self.cmd)

    def evaluate(self):
        """Evaluate.

        Return a Result object, which can be used for pretty-printing.

        """
        result = self.cmd.evaluate()
        return Result(self.input_str, self.cmd, result)


# Helper classes for primitive literals.
def process_int(s, loc, toks):
    return sympy.Integer(toks[0])


__bases = {"0x": 16, "0o": 8, "0b": 2}
def process_intbase(s, loc, toks):
    """Process a string representation of an integer in a base other than 10."""
    base = __bases[toks[0][0]]
    i = int(toks[0][1], base)
    return sympy.Integer(i)


def process_realbase(s, loc, toks):
    """Process a string representation of an real number in a base other
    than 10."""
    int_part = toks[0][0]
    base = __bases[toks[0][0]]
    i = sympy.Integer(int(toks[0][1], base))
    frac_part = toks[0][3]
    exp = len(frac_part)
    r = sympy.Rational(int(frac_part, base), base**exp)
    return i+r


def process_romanint(s, loc, toks):
    _, thousands, hundreds, tens, ones = toks[0]
    i = len(thousands) * 1000
    i += (RomanInt.table[hundreds.upper()]
          + RomanInt.table[tens.upper()]
          + RomanInt.table[ones.upper()])
    return sympy.Integer(i)


class PscicFloat(sympy.Float):
    """TODO: not a subclass of sympy.Float."""
    def __str__(self):
        s = super().__str__()
        # TODO: copy-paste from result.Result._decimal_as_html()
        pre, exp = (s.split("e") + [""])[:2] # ensure length 2 :-(
        pre1, pre2 = pre.split(".")
        pre2 = pre2.rstrip("0")
        if pre2:
            pre = pre1 + "." + pre2
        else:
            pre = pre1
        exp = exp.lstrip("+0")
        if not exp:
            return pre
        return pre + "e" + exp

def process_float(s, loc, toks):
    # TODO: precision is too high. No good solutions come to mind, we     
    # would need to keep them as strings until we know the highest        
    # requested precision, which depends on what we want to output. So    
    # re-calculation for precisions higher then the highest precision     
    # of the previous evaluation is necessary!                            
    #
    # So
    #   * keep as strings on parsing (own Float type)
    #   * somehow register the highest encountered precision
    #   * when evaluating, pass a minimum precision, evaluate Floats
    #     given with less precision to this minimum precision
    #   * store the minimum precision in the result
    #   * if we want a higher precision, we need to re-evaluate, if we
    #     want lower or same, we can use the cached result.
    return PscicFloat(toks[0], 100)


class Operator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def evaluate(self):
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
    def _eval(*args):
        """For every arg, return the evaluated form.

        If an arg is an instance of Operator call .evaluate(),
        otherwise pass it back as is.

        """
        def my_eval(arg):
            if isinstance(arg, Operator):
                return arg.evaluate()
            elif isinstance(arg, sympy.Float) and arg.is_zero:
                # If the float is zero, replace by sympy Integer
                # 0. This will improve some corner cases with division
                # by zero. The reason is, that sympy.Float follows
                # IEEE 754 by returning infinity on division by zero:
                # 1.0/0.0 = oo, -1.0/0.0 = -oo. The problem is, that
                # there is no concept of negative zero, making the
                # whole thing wrong. Further, we do not have a concept
                # of negative zero in this program here, making it
                # double-stupid. Hence return an integer with sane
                # semantics.
                return sympy.Integer(0)
            else:
                return arg
        return tuple(my_eval(arg)
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

    def evaluate(self):
        """Evaluate the expression."""
        retval, = self._eval(self.expr)
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

    def evaluate(self):
        """Evaluate the expression and convert to requested unit."""
        expr, to_unit = self._eval(self.expr, self.to_unit)
        # Wrap if necessary.  # TODO: add sympify() somewhere?
        if isinstance(expr, units.Q_):
            expr = unitbridge.Quantity(expr)
        # Convert anything which has no unit to dimensionless.
        if not isinstance(expr, unitbridge.Quantity):
            expr = unitbridge.Quantity(units.Q_(expr)) # dimensionless
        # Convert units.
        return expr.convert_to(to_unit)


class Equality(Operator):
    """<lhs> = <rhs>, autosolved if possible."""

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

    def evaluate(self):
        """Try to solve."""
        lhs, rhs = self._eval(self.lhs, self.rhs)
        true, false = sympy.S.true, sympy.S.false
        try:
            eq = sympy.Eq(lhs, rhs)
            # Check if we can already say the expression is true or false.
            if eq is true or eq is false:
                return bool(eq)
            # Try harder.
            eq = eq.simplify()
            if eq is true or eq is false:
                return bool(eq)
        except ValueError:
            # Units don't fit, not equal.
            return False
        # Try to solve for x.
        try:
            solutions = sympy.solve(eq, _X)
        except NotImplementedError:
            solutions = []
        if not solutions:
            return eq
        else:
            return Solutions(_X, solutions)


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

    def evaluate(self):
        lhs, rhs = self._eval(self.lhs, self.rhs)
        return lhs + rhs


class Minus(InfixLeftSymbol):
    symbol = "-"

    def evaluate(self):
        lhs, rhs = self._eval(self.lhs, self.rhs)
        return lhs - rhs


class Times(InfixLeftSymbol):
    symbol = "·"

    def evaluate(self):
        lhs, rhs = self._eval(self.lhs, self.rhs)
        return lhs * rhs


class Divide(InfixLeftSymbol):
    symbol = "÷"

    def evaluate(self):
        lhs, rhs = self._eval(self.lhs, self.rhs)
        return lhs / rhs


class IntDivide(InfixLeftSymbol):
    symbol = "//"

    def evaluate(self):
        lhs, rhs = self._eval(self.lhs, self.rhs)
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

    def evaluate(self):
        lhs, rhs = self._eval(self.lhs, self.rhs)
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

    def evaluate(self):
        lhs, = self._eval(self.lhs)
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

    def evaluate(self):
        rhs, = self._eval(self.rhs)
        return -rhs


class PlusSign(PrefixSymbol):
    symbol = "+"

    def evaluate(self):
        rhs, = self._eval(self.rhs)
        return rhs

class Function(Operator):

    @classmethod
    def process(cls, s, loc, toks):
        name = toks[0][0]
        try:
            fn = FunctionList.functions[name]
            argmin = FunctionList.nargs_min[name]
            argmax = FunctionList.nargs_max[name]
        except KeyError:
            raise UnknownFunctionError(name)
        args = toks[0][1:]
        if not (argmin <= len(args) <= argmax):
            raise WrongNumberOfArgumentsError(name, len(args), argmin, argmax)
        return ParseResults([cls(fn.canonical_name, fn.fn, args, fn.args)])

    def __init__(self, fn_s, fn, args, argspec):
        self.fn_s = fn_s
        self.fn = fn
        self.args = args
        self.argspec = argspec

    def __str__(self):
        return "{}({})".format(self.fn_s,
                               ", ".join(str(arg) for arg in self.args))

    def evaluate(self):
        args = self._eval(*self.args)
        args2 = []
        for arg, argspec in zip(args, self.argspec):
            if isinstance(arg, unitbridge.Quantity):
                if not argspec.unit:
                    arg = arg.convert_to("dimensionless").magnitude
                    argtest = arg
                else:
                    argtest = arg.magnitude
            else:
                argtest = arg
            # Check matrix/scalar.
            if isinstance(argtest, sympy.Matrix):
                if not argspec.matrix:
                    raise ValueError(
                        "Function {} does not accept matrices "
                        "or vectors.".format(self.fn_s)
                    )
            elif not argspec.scalar:
                raise ValueError(
                    "Function {} does not accept scalars."
                    "".format(self.fn_s)
                )
            args2.append(arg)
        return self.fn(*args2)


class Constant(Operator):
    # Constants and variables (which are nothing but constants here in
    # terms of implementation).

    _D = collections.namedtuple("_D", ["canonical_name", "value"])

    _constants_and_variables = {
        "e": _D("e", sympy.E),
        "i": _D("i", sympy.I),
        "pi": _D("π", sympy.pi),
        "π": _D("π", sympy.pi),
        "oo": _D("∞", sympy.oo),
        "inf": _D("∞", sympy.oo),
        "∞": _D("∞", sympy.oo),
        "zoo": _D("z∞", sympy.zoo),
        "z∞": _D("z∞", sympy.zoo),

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

    def evaluate(self):
        return self.value


class Unit(Constant):
    # A special kind of constant.

    @classmethod
    def process(cls, s, loc, toks):
        try:
            value = units.ureg(toks[0])
        except units.UndefinedUnitError:
            raise UnknownUnitError(toks[0])
        name = "{:~}".format(value).lstrip("1").lstrip() # remove leading 1
        return cls(name, unitbridge.Quantity(value))

    @classmethod
    def process_dimensionless(cls, s, loc, toks):
        name = "1"
        return cls(name, unitbridge.Quantity(units.ureg.dimensionless))


class Matrix(Operator):

    @classmethod
    def process(cls, s, loc, toks):
        if not toks:
            return cls(0, 0, None)
        rows = len(toks[0])
        cols = len(toks[0][0])
        if any(len(col) != cols
               for col in toks[0]):
            raise VariableLengthRowsError(
                "Rows of matrix have different lengths"
            )
        return cls(rows, cols, toks[0].asList())

    def __init__(self, rows, cols, data):
        self.rows = rows
        self.cols = cols
        self.data = data

    def evaluate(self):
        evaluated = [self._eval(*row)
                     for row in self.data]
        return sympy.Matrix(evaluated)

    def __str__(self):
        return ("["
                + "; ".join(
                    ", ".join(str(cell)
                              for cell in row)
                    for row in self.data
                )
                + "]")

