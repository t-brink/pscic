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

import sympy
from sympy.core import AtomicExpr
from sympy.core.decorators import call_highest_priority

from .units import ureg, Q_


# TODO:
#   * seems to work surprisingly well for so little code
#   * needs __add__ etc. methods to do the right thing (i.e. whatever pint  
#     does). those should return Unit, not Q_!                              
#   * handle this kind of object in the UI parts!
#   * sometimes, the expressions are not evaluated, e.g.                    
#     sin(3 * cm / (5 * in)) becomes sin((3/5 cm / in))                     


class Quantity(AtomicExpr):
    is_positive = True    # make sqrt(m**2) --> m
    is_commutative = True

    __slots__ = ["quantity", "_str_rep"]

    # Use my operators! This may be replaced in the future, have a
    # look at sympy development.
    _op_priority = 10000.0

    def __new__(cls, quantity, **assumptions):
        obj = super().__new__(cls, **assumptions)
        if not isinstance(quantity, Q_):
            raise TypeError("quantity must be a pint Quantity.")
        obj.quantity = quantity
        obj._str_rep = ("{:~}".format(quantity))
        return obj

    def __str__(self):
        return "{:~}".format(self.quantity)

    def _sympystr(self, printer):
        # TODO: parenthesis :-(
        return "(" + str(self) + ")"

    @property
    def magnitude(self):
        return self.quantity.magnitude

    @property
    def units(self):
        return self.quantity.units

    def convert_to(self, unit):
        if isinstance(unit, self.__class__):
            unit = unit.quantity
        return self.__class__(self.quantity.to(unit))

    @call_highest_priority("__rmul__")
    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.quantity * other.quantity)
        else:
            return self.__class__(
                Q_(self.quantity.magnitude * other, self.quantity.units)
            )

    @call_highest_priority("__mul__")
    def __rmul__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(other.quantity * self.quantity)
        else:
            return self.__class__(
                Q_(other * self.quantity.magnitude, self.quantity.units)
            )

    @call_highest_priority("__rmul__")
    def __truediv__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.quantity / other.quantity)
        else:
            return self.__class__(
                Q_(self.quantity.magnitude / other, self.quantity.units)
            )
    __div__ = __truediv__

    @call_highest_priority("__mul__")
    def __rtruediv__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(other.quantity / self.quantity)
        else:
            return self.__class__(
                Q_(other / self.quantity.magnitude, self.quantity.units ** (-1))
            )
    __rdiv__ = __rtruediv__

    @call_highest_priority("__rpow__")
    def __pow__(self, other):
        # Try to unwrap a quantity.
        if isinstance(other, self.__class__):
            other = other.quantity.to(ureg.dimensionless).magnitude
        # Convert number to float if possible.
        if (isinstance(other, sympy.Basic)
            and other.is_number and other.is_real and other.is_finite):
            exp = float(other)
        elif isinstance(other, (int, float)):
            exp = other
        else:
            # Raising to the power of something weird, stay symbolic.
            return super().__pow__(other)
        return self.__class__(self.quantity ** exp)

    @call_highest_priority("__pow__")
    def __rpow__(self, other):
        # Try to convert to dimensionless.
        u = self.quantity.to(ureg.dimensionless).magnitude
        # Raise.
        return other ** u

    def __abs__(self):
        return self.__class__(abs(self.quantity))

    def __eq__(self, other):
        if isinstance(other, (int, float, complex, Q_)):
            return self.quantity == other
        else:
            return super().__eq__(other)

    def __hash__(self):
        return hash(
            (self.__class__.__name__,
             self.quantity.magnitude)
            + tuple(sorted(self.quantity.units.items()))
        )

    def evalf(self, *args, **kwargs):
        return self.__class__(Q_(self.quantity.magnitude.evalf(*args, **kwargs),
                                 self.quantity.units))

def _init():
    # Monkey-patch pint Quantity.
    Q_._sympy_ = lambda self: Quantity(self)


# see also
#   * sympy.physics.units.Unit
#   * sympy.core.expr.AtomicExpr
#   * sympy.core.numbers.Number
#   * sympy.core.symbol.Symbol
