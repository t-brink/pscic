import abc
import math
import collections

from pyparsing import ParseResults

from .exceptions import UnknownFunctionError, UnknownConstantError


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
        return tuple((arg.evaluate() if isinstance(arg, Operator) else arg)
                     for arg in args)


class Expression(Operator):
    """A whole expression (i.e., no equal sign etc., just a term)."""
    def __init__(self, expr):
        self.expr = expr

    @classmethod
    def process(cls, s, loc, toks):
        raise RuntimeError("Do not call this method")

    def __str__(self):
        return str(self.expr)

    def evaluate(self):
        retval, = self._eval(self.expr)
        return retval


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

    def evaluate(self):
        rhs, = self._eval(self.rhs)
        return -rhs


class PlusSign(PrefixSymbol):
    symbol = "+"

    def evaluate(self):
        rhs, = self._eval(self.rhs)
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

    def evaluate(self):
        arg, = self._eval(self.arg)
        return self.fn(arg)
