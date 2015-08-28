import abc
import math

from pyparsing import ParseResults


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

    @classmethod
    def process(cls, s, loc, toks):
        return ParseResults([cls(toks[0][0], toks[0][1])]) # TODO

    def __init__(self, fn, arg):
        # TODO: multiple arguments, actual functions
        self.fn_s = fn
        self.fn = lambda arg: arg # TODO
        self.arg = arg

    def __str__(self):
        return "{}({!s})".format(self.fn_s, self.arg)

    def evaluate(self):
        arg, = self._eval(self.arg)
        return self.fn(arg)
