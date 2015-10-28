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

import sympy

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
        self.assertAlmostEqual(pe("{} · {}", a, b), a * b)
        self.assertAlmostEqual(pe("{} * {}", a, b), a * b)

    def test_divide_int(self):
        a = random.randint(-sys.maxsize, sys.maxsize)
        b = random.randint(-sys.maxsize, sys.maxsize)
        self.assertAlmostEqual(pe("{} ÷ {}", a, b), a / b)
        self.assertAlmostEqual(pe("{} / {}", a, b), a / b)

    def test_divide_float(self):
        a = rand(-1e6, 1e6)
        b = rand(-1e6, 1e6)
        self.assertAlmostEqual(pe("{} ÷ {}", a, b), a / b)
        self.assertAlmostEqual(pe("{} / {}", a, b), a / b)

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
        self.assertAlmostEqual(pe("({}) ** ({})", b, e), b ** e)
        self.assertAlmostEqual(pe("({}) ^ ({})", b, e), b ** e)

    def test_factorial(self):
        self.assertEqual(pe("0!"), 1)
        self.assertEqual(pe("1!"), 1)
        self.assertEqual(pe("2!"), 2)
        a = random.randint(3, 100)
        self.assertEqual(pe("{}!", a), math.factorial(a))
        # Weirdly, there are factorials for rational numbers.
        self.assertAlmostEqual(pe("(1/2)!"), 0.5*math.sqrt(math.pi))


class TestResultType(unittest.TestCase):

    def test_int(self):
        self.assertIsInstance(pe("1"), sympy.Integer)
        self.assertIsInstance(pe("-1"), sympy.Integer)
        self.assertIsInstance(pe("+1"), sympy.Integer)
        self.assertIsInstance(pe("001"), sympy.Integer)
        self.assertEqual(pe("1"), 1)
        self.assertEqual(pe("-1"), -1)
        self.assertEqual(pe("+1"), 1)
        self.assertEqual(pe("001"), 1)

    def test_float(self):
        self.assertIsInstance(pe("1."), sympy.Float)
        self.assertIsInstance(pe("01."), sympy.Float)
        self.assertIsInstance(pe("1.0"), sympy.Float)
        self.assertIsInstance(pe("1e4"), sympy.Float)
        self.assertIsInstance(pe("1e+4"), sympy.Float)
        self.assertIsInstance(pe("1e-4"), sympy.Float)
        self.assertIsInstance(pe("1.e4"), sympy.Float)
        self.assertIsInstance(pe("1.e+4"), sympy.Float)
        self.assertIsInstance(pe("1.e-4"), sympy.Float)
        self.assertIsInstance(pe("1.0e+4"), sympy.Float)
        self.assertIsInstance(pe("1.0e-4"), sympy.Float)
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
        self.assertIsInstance(pe("-1."), sympy.Float)
        self.assertIsInstance(pe("-01."), sympy.Float)
        self.assertIsInstance(pe("-1.0"), sympy.Float)
        self.assertIsInstance(pe("-1e4"), sympy.Float)
        self.assertIsInstance(pe("-1e+4"), sympy.Float)
        self.assertIsInstance(pe("-1e-4"), sympy.Float)
        self.assertIsInstance(pe("-1.e4"), sympy.Float)
        self.assertIsInstance(pe("-1.e+4"), sympy.Float)
        self.assertIsInstance(pe("-1.e-4"), sympy.Float)
        self.assertIsInstance(pe("-1.0e+4"), sympy.Float)
        self.assertIsInstance(pe("-1.0e-4"), sympy.Float)
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
        # Simply ensure that everything which should be integer, is.
        # Do not bother testing for float.
        self.assertIsInstance(pe("+1"), sympy.Integer)
        self.assertIsInstance(pe("-1"), sympy.Integer)
        self.assertIsInstance(pe("1 + 1"), sympy.Integer)
        self.assertIsInstance(pe("1 - 1"), sympy.Integer)
        self.assertIsInstance(pe("1 * 1"), sympy.Integer)
        self.assertIsInstance(pe("1 // 1"), sympy.Integer)
        # not sure if we want to rely on this next one or if it
        # doesn't matter?
        self.assertIsInstance(pe("1 / 1"), sympy.Integer)
        self.assertIsInstance(pe("1 ^ 1"), sympy.Integer)
        self.assertIsInstance(pe("1 ** 1"), sympy.Integer)
        self.assertIsInstance(pe("5!"), sympy.Integer)
        self.assertIsInstance(pe("1. // 1"), sympy.Integer)
        self.assertIsInstance(pe("1 // 1."), sympy.Integer)


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

    def test_multiply_nosign(self):
        self.assertEqual(pe("(1 + 1) · 2m"), 4*ureg.meter)

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
        # Signless multiplication before signed operations.
        self.assertEqual(pe("2cm / 2cm"), 1)

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
        self.assertAlmostEqual(pe("cos(sin(1))"), math.cos(math.sin(1.0)))

    def test_added_functions(self):
        self.assertAlmostEqual(pe("cos(1) + sin(1)"),
                               math.cos(1.0) + math.sin(1.0))

    def test_multiplied_functions(self):
        self.assertAlmostEqual(pe("cos(1) * sin(1)"),
                               math.cos(1.0) * math.sin(1.0))

    def test_function_combinations(self):
        self.assertAlmostEqual(pe("exp(2.3) ^ log(2.3)"),
                               math.exp(2.3) ** math.log(2.3))
        self.assertAlmostEqual(pe("exp(2.3) ** log(2.3)"),
                               math.exp(2.3) ** math.log(2.3))
        self.assertAlmostEqual(pe("-log(2.3)"), -math.log(2.3))
        self.assertAlmostEqual(pe("exp(2.3) + log(2.3)"),
                               math.exp(2.3) + math.log(2.3))
        self.assertAlmostEqual(pe("exp(2.3) - log(2.3)"),
                               math.exp(2.3) - math.log(2.3))
        self.assertAlmostEqual(pe("exp(2.3) * log(2.3)"),
                               math.exp(2.3) * math.log(2.3))
        self.assertAlmostEqual(pe("exp(2.3) / log(2.3)"),
                               math.exp(2.3) / math.log(2.3))
        self.assertAlmostEqual(pe("exp(2.3) // log(2.3)"),
                         int(math.exp(2.3) // math.log(2.3)))
        self.assertAlmostEqual(pe("log(exp(4))!"),
                               math.factorial(math.log(math.exp(4))))

    def test_term_in_function(self):
        self.assertAlmostEqual(pe("sin(1 + 1)"), math.sin(1 + 1))
        self.assertAlmostEqual(pe("sqrt(3 * 2)"), math.sqrt(3 * 2))
        self.assertAlmostEqual(pe("ln(2 ^ 3)"), math.log(2**3))
        self.assertAlmostEqual(pe("sin(3 * cm / (5 * in))"),
                               math.sin(3*ureg.centimeter / (5*ureg.inch)))
        self.assertAlmostEqual(pe("sin(3cm / (5in))"),
                               math.sin(3*ureg.centimeter / (5*ureg.inch)))

    def test_constant_exponents(self):
        self.assertEqual(pe("1m^2"), 1*ureg.meter**2)
        self.assertEqual(pe("1*m^2"), 1*ureg.meter**2)
        self.assertEqual(pe("1m**2"), 1*ureg.meter**2)
        self.assertEqual(pe("1*m**2"), 1*ureg.meter**2)
        self.assertEqual(pe("1*m*m"), 1*ureg.meter**2)
        self.assertEqual(pe("1 m*m"), 1*ureg.meter**2)
        self.assertEqual(pe("1*m m"), 1*ureg.meter**2)
        self.assertEqual(pe("1 m m"), 1*ureg.meter**2)
        self.assertEqual(pe("1 m^-1"), 1/ureg.meter)
        self.assertEqual(pe("1*m^-1"), 1/ureg.meter)
        self.assertEqual(pe("1 m^-2"), ureg.meter**(-2))
        self.assertEqual(pe("1*m^-2"), ureg.meter**(-2))

    def test_intbases(self):
        self.assertEqual(pe("0b110001110101"), 0b110001110101)
        self.assertEqual(pe("0o13741265"), 0o13741265)
        self.assertEqual(pe("0x782FA3BE546C9D10"), 0x782FA3BE546C9D10)

    def test_realbases(self):
        # hex
        self.assertAlmostEqual(pe("0xA.8"), 10.5)
        self.assertAlmostEqual(pe("0x0.5555555555555555555555555"),
                               0.3333333333333333333333333333)
        self.assertAlmostEqual(pe("0x0.4"), 0.25)
        self.assertAlmostEqual(pe("0x0.2"), 0.125)
        self.assertAlmostEqual(pe("0x0.1"), 0.0625)
        # oct
        self.assertAlmostEqual(pe("0o1.01"), 1+1/64)
        self.assertAlmostEqual(pe("0o0.1"), 1/8)
        self.assertAlmostEqual(pe("0o0.2"), 1/4)
        self.assertAlmostEqual(pe("0o0.4"), 1/2)
        self.assertAlmostEqual(pe("0o0.5"), 5/8)
        self.assertAlmostEqual(pe("0o0.6"), 3/4)
        self.assertAlmostEqual(pe("0o0.7"), 7/8)
        # bin
        self.assertAlmostEqual(pe("0b1.1"), 3/2)
        self.assertAlmostEqual(pe("0b0.1"), 1/2)
        self.assertAlmostEqual(pe("0b0.01"), 1/4)
        self.assertAlmostEqual(pe("0b0.11"), 3/4)
        self.assertAlmostEqual(pe("0b0.10"), 1/2)

class TestUnits(unittest.TestCase):
    def test_conversion(self):
        self.assertEqual(pe("1*in to cm"), 1*ureg.inch.to(ureg.centimeter))
        self.assertEqual(pe("1in to cm"), 1*ureg.inch.to(ureg.centimeter))
        self.assertEqual(pe("1/in to 1/cm"), (1 / ureg.inch).to(1/ureg.centimeter))

    def test_null_conversion(self):
        self.assertEqual(pe("7124 to 1"), 7124)

    def test_exponents(self):
        self.assertEqual(pe("(1*m^2)"), 1*ureg.meter**2)
        self.assertEqual(pe("sqrt(1*m^2)"), 1*ureg.meter)
        # Weird, but must be legal.
        self.assertEqual(pe("1m^pi"), 1*ureg.meter**math.pi)


class TestFunctions(unittest.TestCase):
    def test_trig(self):
        a = rand(-1e6, 1e6)
        # sin
        self.assertEqual(pe("sin(0)"), 0)
        self.assertEqual(pe("sin(pi/2)"), 1)
        self.assertEqual(pe("sin(pi)"), 0)
        self.assertEqual(pe("sin(3pi/2)"), -1)
        self.assertEqual(pe("sin(2pi)"), 0)
        self.assertAlmostEqual(pe("sin({})", a), math.sin(a))
        # cos
        self.assertEqual(pe("cos(0)"), 1)
        self.assertEqual(pe("cos(pi/2)"), 0)
        self.assertEqual(pe("cos(pi)"), -1)
        self.assertEqual(pe("cos(3pi/2)"), 0)
        self.assertEqual(pe("cos(2pi)"), 1)
        self.assertAlmostEqual(pe("cos({})", a), math.cos(a))
        # tan
        self.assertEqual(pe("tan(0)"), 0)
        self.assertEqual(pe("tan(pi/4)"), 1)
        self.assertEqual(pe("tan(-pi/4)"), -1)
        self.assertEqual(pe("tan(pi)"), 0)
        self.assertEqual(pe("tan(-pi)"), 0)

    def test_units(self):
        self.assertEqual(pe("sqrt(1m^2)"), 1*ureg.meter)
        with self.assertRaises(ValueError):
            pe("sin(2cm)")
        with self.assertRaises(ValueError):
            pe("ceil(2cm)")
        self.assertEqual(pe("abs(-2in)"), 2*ureg.inch)


class TestEquality(unittest.TestCase):
    def test_identities(self):
        #
        self.assertEqual(pe("cos(x) + i*sin(x) = exp(x*i)"), True)
        # pq-formula.
        solutions = sorted(pe("x**2 + 3*x - 4 = 0").solutions)
        self.assertEqual(len(solutions), 2)
        self.assertAlmostEqual(solutions[0], -4)
        self.assertAlmostEqual(solutions[1], 1)
