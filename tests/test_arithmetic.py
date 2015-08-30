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

import unittest
import random
import sys
import math

from psciclib.parseexpr import parse
from psciclib.units import ureg


# Helpers.
def pe(s, *args):
    print(s.format(*args))
    return parse(s.format(*args)).evaluate()

def rand(min, max):
    return random.random() * (max-min) + min


class TestStandaloneExpressions(unittest.TestCase):

    def test_negsign_int(self):
        a = random.randint(-sys.maxsize, sys.maxsize)
        self.assertEqual(pe("-{}", a), -a)

    def test_negsign_float(self):
        a = rand(-1e6, 1e6)
        self.assertEqual(pe("-{}", a), -a)

    def test_possign_int(self):
        a = random.randint(-sys.maxsize, sys.maxsize)
        self.assertEqual(pe("+{}", a), +a)

    def test_possign_float(self):
        a = rand(-1e6, 1e6)
        self.assertEqual(pe("+{}", a), +a)

    def test_plus_int(self):
        a = random.randint(-sys.maxsize, sys.maxsize)
        b = random.randint(-sys.maxsize, sys.maxsize)
        self.assertEqual(pe("{} + {}", a, b), a + b)

    def test_plus_float(self):
        a = rand(-1e6, 1e6)
        b = rand(-1e6, 1e6)
        self.assertEqual(pe("{} + {}", a, b), a + b)

    def test_minus_int(self):
        a = random.randint(-sys.maxsize, sys.maxsize)
        b = random.randint(-sys.maxsize, sys.maxsize)
        self.assertEqual(pe("{} - {}", a, b), a - b)

    def test_minus_float(self):
        a = rand(-1e6, 1e6)
        b = rand(-1e6, 1e6)
        self.assertEqual(pe("{} - {}", a, b), a - b)

    def test_multiply_int(self):
        a = random.randint(-sys.maxsize, sys.maxsize)
        b = random.randint(-sys.maxsize, sys.maxsize)
        self.assertEqual(pe("{} · {}", a, b), a * b)
        self.assertEqual(pe("{} * {}", a, b), a * b)

    def test_multiply_float(self):
        a = rand(-1e6, 1e6)
        b = rand(-1e6, 1e6)
        self.assertEqual(pe("{} · {}", a, b), a * b)
        self.assertEqual(pe("{} * {}", a, b), a * b)

    def test_divide_int(self):
        a = random.randint(-sys.maxsize, sys.maxsize)
        b = random.randint(-sys.maxsize, sys.maxsize)
        self.assertEqual(pe("{} ÷ {}", a, b), a / b)
        self.assertEqual(pe("{} / {}", a, b), a / b)

    def test_divide_float(self):
        a = rand(-1e6, 1e6)
        b = rand(-1e6, 1e6)
        self.assertEqual(pe("{} ÷ {}", a, b), a / b)
        self.assertEqual(pe("{} / {}", a, b), a / b)

    def test_intdivide_int(self):
        a = random.randint(-sys.maxsize, sys.maxsize)
        b = random.randint(-sys.maxsize, sys.maxsize)
        self.assertEqual(pe("{} // {}", a, b), a // b)

    def test_intdivide_float(self):
        a = rand(-1e6, 1e6)
        b = rand(-1e6, 1e6)
        self.assertEqual(pe("{} // {}", a, b), int(a // b))

    def test_exponent_int(self):
        b = random.randint(-500, 500)
        e = random.randint(-10, 10)
        self.assertEqual(pe("({}) ** ({})", b, e), b ** e)
        self.assertEqual(pe("({}) ^ ({})", b, e), b ** e)

    def test_exponent_float(self):
        b = rand(-500.0, 500.0)
        e = rand(-10.0, 10.0)
        self.assertEqual(pe("({}) ** ({})", b, e), b ** e)
        self.assertEqual(pe("({}) ^ ({})", b, e), b ** e)

    def test_factorial(self):
        self.assertEqual(pe("0!"), 1)
        self.assertEqual(pe("1!"), 1)
        self.assertEqual(pe("2!"), 2)
        a = random.randint(3, 100)
        self.assertEqual(pe("{}!", a), math.factorial(a))


class TestResultType(unittest.TestCase):

    def test_int(self):
        self.assertIsInstance(pe("1"), int)
        self.assertIsInstance(pe("-1"), int)
        self.assertIsInstance(pe("+1"), int)
        self.assertIsInstance(pe("001"), int)
        self.assertEqual(pe("1"), 1)
        self.assertEqual(pe("-1"), -1)
        self.assertEqual(pe("+1"), 1)
        self.assertEqual(pe("001"), 1)

    def test_float(self):
        self.assertIsInstance(pe("1."), float)
        self.assertIsInstance(pe("01."), float)
        self.assertIsInstance(pe("1.0"), float)
        self.assertIsInstance(pe("1e4"), float)
        self.assertIsInstance(pe("1e+4"), float)
        self.assertIsInstance(pe("1e-4"), float)
        self.assertIsInstance(pe("1.e4"), float)
        self.assertIsInstance(pe("1.e+4"), float)
        self.assertIsInstance(pe("1.e-4"), float)
        self.assertIsInstance(pe("1.0e+4"), float)
        self.assertIsInstance(pe("1.0e-4"), float)
        self.assertEqual(pe("1."), 1.0)
        self.assertEqual(pe("01."), 1.0)
        self.assertEqual(pe("1.0"), 1.0)
        self.assertEqual(pe("1e4"), 1e4)
        self.assertEqual(pe("1e+4"), 1e4)
        self.assertEqual(pe("1e-4"), 1e-4)
        self.assertEqual(pe("1.e4"), 1e4)
        self.assertEqual(pe("1.e+4"), 1e4)
        self.assertEqual(pe("1.e-4"), 1e-4)
        self.assertEqual(pe("1.0e+4"), 1e4)
        self.assertEqual(pe("1.0e-4"), 1e-4)
        self.assertIsInstance(pe("-1."), float)
        self.assertIsInstance(pe("-01."), float)
        self.assertIsInstance(pe("-1.0"), float)
        self.assertIsInstance(pe("-1e4"), float)
        self.assertIsInstance(pe("-1e+4"), float)
        self.assertIsInstance(pe("-1e-4"), float)
        self.assertIsInstance(pe("-1.e4"), float)
        self.assertIsInstance(pe("-1.e+4"), float)
        self.assertIsInstance(pe("-1.e-4"), float)
        self.assertIsInstance(pe("-1.0e+4"), float)
        self.assertIsInstance(pe("-1.0e-4"), float)
        self.assertEqual(pe("-1."), -1.0)
        self.assertEqual(pe("-01."), -1.0)
        self.assertEqual(pe("-1.0"), -1.0)
        self.assertEqual(pe("-1e4"), -1e4)
        self.assertEqual(pe("-1e+4"), -1e4)
        self.assertEqual(pe("-1e-4"), -1e-4)
        self.assertEqual(pe("-1.e4"), -1e4)
        self.assertEqual(pe("-1.e+4"), -1e4)
        self.assertEqual(pe("-1.e-4"), -1e-4)
        self.assertEqual(pe("-1.0e+4"), -1e4)
        self.assertEqual(pe("-1.0e-4"), -1e-4)

    def test_operations(self):
        self.assertIsInstance(pe("+1"), int)
        self.assertIsInstance(pe("-1"), int)
        self.assertIsInstance(pe("1 + 1"), int)
        self.assertIsInstance(pe("1 - 1"), int)
        self.assertIsInstance(pe("1 * 1"), int)
        self.assertIsInstance(pe("1 // 1"), int)
        self.assertIsInstance(pe("1 / 1"), float)
        self.assertIsInstance(pe("1 ^ 1"), int)
        self.assertIsInstance(pe("1 ** 1"), int)
        self.assertIsInstance(pe("5!"), int)
        self.assertIsInstance(pe("+1."), float)
        self.assertIsInstance(pe("-1."), float)
        self.assertIsInstance(pe("1. + 1"), float)
        self.assertIsInstance(pe("1 + 1."), float)
        self.assertIsInstance(pe("1. - 1"), float)
        self.assertIsInstance(pe("1 - 1."), float)
        self.assertIsInstance(pe("1. * 1."), float)
        self.assertIsInstance(pe("1 * 1."), float)
        self.assertIsInstance(pe("1. // 1"), int)
        self.assertIsInstance(pe("1 // 1."), int)
        self.assertIsInstance(pe("1. / 1"), float)
        self.assertIsInstance(pe("1 / 1."), float)
        self.assertIsInstance(pe("1. ^ 1"), float)
        self.assertIsInstance(pe("1 ^ 1."), float)
        self.assertIsInstance(pe("1. ** 1"), float)
        self.assertIsInstance(pe("1 ** 1."), float)
        self.assertIsInstance(pe("5.!"), int)


class TestParser(unittest.TestCase):

    def test_chain_plus(self):
        s = "1 + 2 + 3 + 4 + 5"
        self.assertEqual(pe(s), eval(s))

    def test_chain_minus(self):
        s = "1 - 2 - 3 - 4 - 5"
        self.assertEqual(pe(s), eval(s))

    def test_chain_plusminus(self):
        s = "1 + 2 - 3 + 4 - 5"
        self.assertEqual(pe(s), eval(s))

    def test_chain_multiply(self):
        s = "1 * 2 * 3 * 4 * 5"
        self.assertEqual(pe(s), eval(s))

    def test_chain_divide(self):
        s = "1 / 2 / 3 / 4 / 5"
        self.assertEqual(pe(s), eval(s))

    def test_chain_intdivide(self):
        s = "100 // 2 // 2 // 2"
        self.assertEqual(pe(s), eval(s))

    def test_chain_multiplydivide(self):
        s = "10 * 2 / 3 * 4 // 5"
        self.assertEqual(pe(s), eval(s))

    def test_chain_sign(self):
        self.assertEqual(pe("-----1"), -1)
        self.assertEqual(pe("+++++1"), +1)
        self.assertEqual(pe("+-+-+1"), +1)
        self.assertEqual(pe("-+-+-1"), -1)

    def test_chain_factorial(self):
        self.assertEqual(pe("3!!!"),
                         math.factorial(math.factorial(math.factorial(3))))

    def test_chain_exponent(self):
        self.assertEqual(pe("2^3^4"), 2**3**4)
        self.assertEqual(pe("2**3**4"), 2**3**4)
        self.assertEqual(pe("2^3**4"), 2**3**4)
        self.assertEqual(pe("2**3^4"), 2**3**4)

    def test_precedence(self):
        # Factorial
        self.assertEqual(pe("2^3!"), 2**math.factorial(3))
        self.assertEqual(pe("2**3!"), 2**math.factorial(3))
        self.assertEqual(pe("-3!"), -math.factorial(3))
        self.assertEqual(pe("2*3!"), 2*math.factorial(3))
        self.assertEqual(pe("2/3!"), 2/math.factorial(3))
        self.assertEqual(pe("2//3!"), 2//math.factorial(3))
        self.assertEqual(pe("2+3!"), 2+math.factorial(3))
        self.assertEqual(pe("2-3!"), 2-math.factorial(3))
        # Exponent
        self.assertEqual(pe("-2^2"), -4)
        self.assertEqual(pe("(-2)^2"), 4)
        self.assertEqual(pe("5*6^2"), 180)
        self.assertEqual(pe("32/4^2"), 2.0)
        self.assertEqual(pe("32//4^2"), 2)
        self.assertEqual(pe("1 + 4^2"), 17)
        self.assertEqual(pe("1 - 4^2"), -15)
        # Sign
        self.assertEqual(pe("5 * -2"), -10)
        self.assertEqual(pe("5 / -2"), -5/2)
        self.assertEqual(pe("5 // -2"), -5//2)
        self.assertEqual(pe("-1 + -2"), -3)
        self.assertEqual(pe("-1 - -2"), 1)
        # Multiplication / addition
        self.assertEqual(pe("1 + 2 * 3"), 7)
        self.assertEqual(pe("1 + 3 / 3"), 2)
        self.assertEqual(pe("1 + 3 // 3"), 2)
        self.assertEqual(pe("1 - 2 * 3"), -5)
        self.assertEqual(pe("1 - 3 / 3"), 0)
        self.assertEqual(pe("1 - 3 // 3"), 0)

    def test_exponent_and_sign(self):
        self.assertEqual(pe("3 ^ 4"), 3 ** 4)
        self.assertEqual(pe("-3 ^ 4"), -(3 ** 4))
        self.assertEqual(pe("3 ^ -4"), 3 ** (-4))
        self.assertEqual(pe("-3 ^ -4"), -(3 ** (-4)))
        self.assertEqual(pe("3 ^ 4"), 3 ** 4)
        self.assertEqual(pe("+3 ^ 4"), 3 ** 4)
        self.assertEqual(pe("3 ^ +4"), 3 ** 4)
        self.assertEqual(pe("+3 ^ +4"), 3 ** 4)
        #
        self.assertEqual(pe("3 ** 4"), 3 ** 4)
        self.assertEqual(pe("-3 ** 4"), -(3 ** 4))
        self.assertEqual(pe("3 ** -4"), 3 ** (-4))
        self.assertEqual(pe("-3 ** -4"), -(3 ** (-4)))
        self.assertEqual(pe("3 ** 4"), 3 ** 4)
        self.assertEqual(pe("+3 ** 4"), 3 ** 4)
        self.assertEqual(pe("3 ** +4"), 3 ** 4)
        self.assertEqual(pe("+3 ** +4"), 3 ** 4)
        #
        self.assertEqual(pe("3 ^ --4"), 3 ** 4)
        self.assertEqual(pe("-3 ^ --4"), -(3 ** 4))
        self.assertEqual(pe("3 ^ -+4"), 3 ** (-4))
        self.assertEqual(pe("-3 ^ +-4"), -(3 ** (-4)))
        self.assertEqual(pe("3 ^ ++4"), 3 ** 4)
        self.assertEqual(pe("+3 ^ ++4"), 3 ** 4)
        #
        self.assertEqual(pe("3 ** --4"), 3 ** 4)
        self.assertEqual(pe("-3 ** --4"), -(3 ** 4))
        self.assertEqual(pe("3 ** -+4"), 3 ** (-4))
        self.assertEqual(pe("-3 ** +-4"), -(3 ** (-4)))
        self.assertEqual(pe("3 ** ++4"), 3 ** 4)
        self.assertEqual(pe("+3 ** ++4"), 3 ** 4)
        #
        self.assertEqual(pe("3 ^ -4 ^ -4"), 3 ** -(4 ** (-4)))
        self.assertEqual(pe("3 ** -4 ** -4"), 3 ** -(4 ** (-4)))
        self.assertEqual(pe("3 ^ -4 ** -4"), 3 ** -(4 ** (-4)))

    def test_parentheses(self):
        self.assertEqual(pe("(1)"), 1)
        self.assertEqual(pe("(((1)))"), 1)
        self.assertEqual(pe("(+1)"), 1)
        self.assertEqual(pe("(-1)"), -1)
        self.assertEqual(pe("(1+1)"), 2)
        self.assertEqual(pe("((1+1) * 2) ^ 3"), 64)
        self.assertEqual(pe("-(1+1)"), -2)

    def test_nested_functions(self):
        self.assertEqual(pe("cos(sin(1))"), math.cos(math.sin(1.0)))

    def test_added_functions(self):
        self.assertEqual(pe("cos(1) + sin(1)"), math.cos(1.0) + math.sin(1.0))

    def test_multiplied_functions(self):
        self.assertEqual(pe("cos(1) * sin(1)"), math.cos(1.0) * math.sin(1.0))

    def test_function_combinations(self):
        self.assertEqual(pe("exp(2.3) ^ log(2.3)"), math.exp(2.3) ** math.log(2.3))
        self.assertEqual(pe("exp(2.3) ** log(2.3)"), math.exp(2.3) ** math.log(2.3))
        self.assertEqual(pe("-log(2.3)"), -math.log(2.3))
        self.assertEqual(pe("exp(2.3) + log(2.3)"), math.exp(2.3) + math.log(2.3))
        self.assertEqual(pe("exp(2.3) - log(2.3)"), math.exp(2.3) - math.log(2.3))
        self.assertEqual(pe("exp(2.3) * log(2.3)"), math.exp(2.3) * math.log(2.3))
        self.assertEqual(pe("exp(2.3) / log(2.3)"), math.exp(2.3) / math.log(2.3))
        self.assertEqual(pe("exp(2.3) // log(2.3)"),
                         int(math.exp(2.3) // math.log(2.3)))
        self.assertEqual(pe("log(exp(4))!"), math.factorial(math.log(math.exp(4))))

    def test_term_in_function(self):
        self.assertEqual(pe("sin(1 + 1)"), math.sin(1 + 1))
        self.assertEqual(pe("sqrt(3 * 2)"), math.sqrt(3 * 2))
        self.assertEqual(pe("ln(2 ^ 3)"), math.log(2**3))
        self.assertEqual(pe("sin(3 * cm / (5 * in))"),
                         math.sin(3*ureg.centimeter / (5*ureg.inch)))
        self.assertEqual(pe("sin(3cm / (5in))"),
                         math.sin(3*ureg.centimeter / (5*ureg.inch)))

class TestFunctions(unittest.TestCase):
    pass # TODO                     
