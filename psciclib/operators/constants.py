# Copyright (C) 2016  Tobias Brink
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

from .. import units
from .. import unitbridge

_X = sympy.Symbol("x")


class ConstantList:

    _c = collections.namedtuple(
        "_c",
        ["canonical_name", "aliases", "value", "unit"]
    )
    _c.names = lambda self: (self.canonical_name,) + self.aliases

    _constants = [
        _c("e", (), sympy.E, None),
        _c("i", (), sympy.I, None),
        _c("π", ("pi",), sympy.pi, None),
        _c("∞", ("oo", "inf"), sympy.oo, None),
        _c("z∞", ("zoo",), sympy.zoo, None),

        # Variables.
        _c("x", (), _X, None),

        # Physical constants. CODATA 2014.
        #
        # TODO: sympy floats                                   
        # TODO: double-check                                   
        _c("c", ("c0", "lightspeed", "speed_of_light"),
           299792458, "m/s"),                         # exact
        _c("µ0", ("mu0", "magnetic_constant",),
           4e-7*sympy.pi, "N A^-2"),                  # exact
        _c("ε0", ("epsilon0", "electric_constant"),
           1/(4e-7*sympy.pi*(299792458)**2), "F/m"),  # exact
        _c("G", ("gravitational_constant", "newtonian_constant_of_gravitation"),
           6.67408e-11, "m^3 kg^-1 s^-2"),
        _c("h", ("planck", "planck_constant"),
           6.626070040e-34, "J s"),
        _c("ħ", ("hbar", "planck2pi"),
           1.054571800e-34, "J s"),
        _c("ec", ("q", "elementary_charge"),
           1.6021766208e-19, "C"),
        _c("kB", ("boltzmann",),
           1.38064852e-23, "J/K"),

        # Atomic weights (weight because IUPAC says that atomic mass
        # refers to the mass of a single atom, while weight is
        # averaged over isotopes according to their abundance).
        # http://www.ciaaw.org/ (IUPAC)
        #
        # Data from Meija et al., Pure Appl. Chem. 88, 265 (2016)
        #
        # In case there is a range of masses, I used the average
        # (explicitly calculated, see e.g. H), perhaps I have a better
        # idea in the future.
        #
        # TODO: sympy floats                                   
        # TODO: double-check                                   
        _c("m_H", (), (1.00784 + 1.00811)/2, "u"),
        _c("m_He", (), 4.002602, "u"),
        _c("m_Li", (), (6.938 + 6.997)/2, "u"),
        # ....

        # Isotope masses.
        # http://www.ciaaw.org/ (IUPAC)
        #
        # TODO: sympy floats                                   
        # TODO: double-check                                   
        _c("m_H1", (), 1.0078250322, "u"),
        _c("m_H2", (), 2.0141017781, "u"),
        # ....

        # Isotope abundances.
        # http://www.ciaaw.org/ (IUPAC)
        # TODO if I'm really bored.
    ]

    @classmethod
    def init(cls):
        cls.constants = {}
        cls.canonical_name = {}
        for const in cls._constants:
            v = (const.value
                 if const.unit is None
                 else unitbridge.Quantity(const.value * units.ureg(const.unit)))
            for name in const.names():
                cls.constants[name] = v
                cls.canonical_name[name] = const.canonical_name

ConstantList.init()
