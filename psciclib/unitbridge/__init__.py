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

"""This module contains a sympy wrapper for pint."""

from sympy import sympify
from sympy.core import AtomicExpr

from ..units import Q_


# TODO:
#   * seems to work surprisingly well for so little code
#   * needs to register to sympify to do it automatically
#   * needs __add__ etc. methods to do the right thing (i.e. whatever pint
#     does). those should return Unit, not Q_!
#   * handle this kind of object in the UI parts!


def sympify_pint_quantity(q):
    m = sympify(q.magnitude)
    u = Unit(Q_(1, q.units))
    return m*u


class Unit(AtomicExpr):
    is_positive = True    # make sqrt(m**2) --> m
    is_commutative = True

    __slots__ = ["unit", "abbrev"]

    def __new__(cls, unit, **assumptions):
        obj = super().__new__(cls, **assumptions)
        if not isinstance(unit, Q_):
            raise TypeError("unit must be a pint Quantity.")
        obj.unit = unit
        obj.abbrev = ("{:H~}".format(unit)).lstrip("1").lstrip() # strip "1 "-prefix!
        return obj

# see also
#   * sympy.physics.units.Unit
#   * sympy.core.expr.AtomicExpr
#   * sympy.core.numbers.Number
#   * sympy.core.symbol.Symbol
