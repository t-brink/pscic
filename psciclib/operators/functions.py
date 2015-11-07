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

import collections

import sympy


class ArgCap:
    """What can this function argument accept?

    scalar: a number, if false (unusual) will raise ValueError
            on receiving one
    matrix: a matrix or vector, if false will raise ValueError
            on receiving one
    unit: a scalar or matrix with a unit of measurement attached,
          will try to convert to dimensionless if false

    """
    def __init__(self, scalar, matrix, unit, optional=False):
        self.scalar = scalar
        self.matrix = matrix
        self.unit = unit
        self.optional = optional


class FunctionList:

    _f = collections.namedtuple(
        "_f",
        ["canonical_name", "aliases", "fn", "args"]
    )
    _f.names = lambda self: (self.canonical_name,) + self.aliases

    # TODO: overloading by type??
    #    e.g. "abs(1)" -> abs,  "abs([1,2,3])" -> norm ?
    _functions = [
        # Trigonometric functions.
        _f("sin", (), sympy.sin, (ArgCap(True, False, False),)),
        _f("cos", (), sympy.cos, (ArgCap(True, False, False),)),
        _f("tan", (), sympy.tan, (ArgCap(True, False, False),)),
        _f("cot", (), sympy.cot, (ArgCap(True, False, False),)),
        _f("sec", (), sympy.sec, (ArgCap(True, False, False),)),
        _f("cosec", ("csc",), sympy.csc, (ArgCap(True, False, False),)),
        # Inverse trigonometric functions.
        _f("arcsin", ("asin",), sympy.asin, (ArgCap(True, False, False),)),
        _f("arccos", ("acos",), sympy.acos, (ArgCap(True, False, False),)),
        _f("arctan", ("atan",), sympy.atan, (ArgCap(True, False, False),)),
        _f("arccot", ("acot",), sympy.acot, (ArgCap(True, False, False),)),
        _f("arcsec", ("asec",), sympy.asec, (ArgCap(True, False, False),)),
        _f("arccosec", ("acsc", "arccsc", "acosec", "arccosec"),
           sympy.asec, (ArgCap(True, False, False),)),
        # Hyperbolic functions.
        _f("sinh", (), sympy.sinh, (ArgCap(True, False, False),)),
        _f("cosh", (), sympy.cosh, (ArgCap(True, False, False),)),
        _f("tanh", (), sympy.tanh, (ArgCap(True, False, False),)),
        _f("coth", (), sympy.coth, (ArgCap(True, False, False),)),
        _f("sech", (), lambda x: 1/sympy.cosh(x),
           (ArgCap(True, False, False),)),
        _f("cosech", ("csch",), lambda x: 1/sympy.sinh(x),
           (ArgCap(True, False, False),)),
        # Inverse hyperbolic functions.
        _f("arsinh", ("asinh", ), sympy.asinh, (ArgCap(True, False, False),)),
        _f("arcosh", ("acosh", ), sympy.acosh, (ArgCap(True, False, False),)),
        _f("artanh", ("atanh", ), sympy.atanh, (ArgCap(True, False, False),)),
        _f("arcoth", ("acoth", ), sympy.acoth, (ArgCap(True, False, False),)),
        _f("arsech", ("asech", ), lambda x: sympy.acosh(1/x),
           (ArgCap(True, False, False),)),
        _f("arcosech", ("acsch", "arcsch", "acosech", "arcosech"),
           lambda x: sympy.asinh(1/x), (ArgCap(True, False, False),)),
        # e-function related.
        _f("exp", (), sympy.exp, (ArgCap(True, False, False),)),
        _f("ln", (), sympy.log, (ArgCap(True, False, False),)),
        _f("log", (), sympy.log,
           (ArgCap(True, False, False), ArgCap(True, False, False, True))),
        _f("log10", (), lambda x: sympy.log(x, 10),
           (ArgCap(True, False, False),)),
        _f("log2", (), lambda x: sympy.log(x, 2),
           (ArgCap(True, False, False),)),
        # Square root.
        _f("√", ("sqrt",), lambda x: x**sympy.Rational(1/2),
           (ArgCap(True, True, True),)),
        # Error function.
        _f("erf", (), sympy.erf, (ArgCap(True, False, False),)),
        _f("erfc", (), sympy.erfc, (ArgCap(True, False, False),)),
        # Misc.
        #TODO: support absolutes for matrices in the sense of norm()   
        _f("abs", (), abs, (ArgCap(True, False, True),)),
        _f("floor", (), sympy.floor, (ArgCap(True, False, False),)),
        _f("ceil", ("ceiling",), sympy.ceiling, (ArgCap(True, False, False),)),
        # Geometry.
        #TODO: should those only take lengths??  
        _f("circle_area", (), lambda r: sympy.pi * r**2,
           (ArgCap(True, False, True),)),
        _f("circle_circumference", ("circle_circ", ),
           lambda r: 2 * sympy.pi * r,
           (ArgCap(True, False, True),)),
        _f("sphere_volume", ("sphere_vol", ),
           lambda r: sympy.Rational(4,3) * sympy.pi * r**3,
           (ArgCap(True, False, True),)),
        _f("sphere_surface", ("sphere_surf", ),
           lambda r: 4 * sympy.pi * r**2,
           (ArgCap(True, False, True),)),
    ]

    @classmethod
    def init(cls):
        cls.functions = {}
        cls.nargs_min = {}
        cls.nargs_max = {}
        for func in cls._functions:
            for name in func.names():
                cls.functions[name] = func
                n = 0
                done = False
                for arg in func.args:
                    if arg.optional:
                        done = True
                    elif done:
                        raise ValueError("Non-optional arg after optional arg")
                    else:
                        n += 1
                cls.nargs_min[name] = n
                cls.nargs_max[name] = len(func.args)

# TODO: init here?
FunctionList.init()
