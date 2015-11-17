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

"""Hints for certain types of results."""


_zoo_hint = (
    "Your result contains z∞ (complex infinity) which most likely "
    "means that some operation in your expression is undefined "
    "(for example a division by zero)."
)
_eq_hint = (
    "The equality could not be solved or tested for truth and is "
    "returned in simplified form."
)
_numerical_solution_hint = (
    "The solution could not be obtained analytically. The given solution "
    "is obtained numerically and may not be the only solution. "
    "Play with the starting value to find other solutions. "
    "TODO: UI to input starting value."
)
_unit_hint = (
    "The precision of calculations with units may in some cases be less "
    "than requested. This is a bug that will be fixed in the future."
)

def get_hints(result, digits, is_numerical):
    hints = set()
    if is_numerical:
        hints.add(_numerical_solution_hint)
    from .result import Solutions
    if isinstance(result, bool):
        # No hints here.
        pass
    elif isinstance(result, Solutions):
        # A bunch of solutions.
        for sol in result.solutions:
            hints |= get_hints(sol, digits, is_numerical)
    else:
        # A single result.
        import sympy
        from .unitbridge import Quantity
        atoms = result.atoms()
        for atom in atoms:
            is_q = isinstance(atom, Quantity)
            if ((atom is sympy.zoo)
                or (is_q and sympy.zoo in atom.magnitude.atoms())):
                hints.add(_zoo_hint)
            if is_q and digits > 14: # 15 should be about 64bit float precision?
                hints.add(_unit_hint)
        if isinstance(result, sympy.Equality):
            hints.add(_eq_hint)
    return hints
