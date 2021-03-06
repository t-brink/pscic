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

    __c = 299792458 # m/s
    __mu0 = 4e-7 * sympy.pi # N/A²
    __eps0 = 1/(__mu0*__c**2) # F/m
    __G = 6.67408e-11 # m³ / kg·s²
    __h = 6.626070040e-34 # Js
    __hbar = __h / (2 * sympy.pi) # Js
    __ec = 1.6021766208e-19 # C
    __kB = 1.38064852e-23 # J/K
    __me = 9.10938356e-31 # kg
    __mp = 1.672621898e-27 # kg
    __alpha = __ec**2 / (2 * __eps0 * __h * __c) # dimensionless
    __NA = 6.022140857e23 # mol^-1
    __sigma = (sympy.pi**2 / 60) * __kB**4 / (__hbar**3 * __c**2) # W / m²K^4

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
           __c, "m/s"),                         # exact
        _c("µ0", ("mu0", "magnetic_constant"),
           __mu0, "N A^-2"),                    # exact
        _c("ε₀", ("ε0", "epsilon0", "electric_constant"),
           __eps0, "F/m"),                      # exact
        _c("G", ("gravitational_constant", "newtonian_constant_of_gravitation"),
           __G, "m^3 kg^-1 s^-2"),
        _c("h", ("planck", "planck_constant"),
           __h, "J s"),
        _c("ħ", ("hbar", "planck2pi"),
           __hbar, "J s"),
        _c("ec", ("q", "elementary_charge"),
           __ec, "C"),
        _c("kB", ("boltzmann",),
           __kB, "J/K"),
        _c("Φ₀", ("Φ0", "magnetic_flux_quantum"),
           __h / (2 * __ec), "Wb"),
        _c("G₀", ("G0", "conductance_quantum"),
           2 * __ec**2 / __h, "S"),
        _c("me", ("m_e", "electron_mass"),
           __me, "kg"),
        _c("mp", ("m_p", "proton_mass"),
           __mp, "kg"),
        _c("α", ("alpha", "fine_structure_constant"),
           __alpha, None),
        _c("R∞", ("Rinf", "rydberg_constant"),
           __alpha**2 * __me * __c / (2 * __h), "m^-1"),
        _c("NA", ("avogadro", "avogadro_constant"),
           __NA, "mol^-1"), # in fact 1/mol, let's see if it blows up!
        _c("faraday", ("faraday_constant",),
           __NA * __ec, "C/mol"),
        _c("R", ("gas_constant", "molar_gas_constant"),
           __kB * __NA, "J / (mol K)"),
        _c("σ", ("sigma", "stefan_boltzmann_constant"),
           __sigma, "W / (m^2 K^4)"),

        # Atomic weights (weight because IUPAC says that atomic mass
        # refers to the mass of a single atom, while weight is
        # averaged over isotopes according to their abundance).
        # http://www.ciaaw.org/ (IUPAC)
        #
        # Data from Meija et al., Pure Appl. Chem. 88, 265 (2016);
        # Table 1.
        #
        # In case there is a range of masses, I used the
        # "conventional" value from Table 3.
        #
        # TODO: sympy floats                                   
        # TODO: double-check                                   
        _c("m_H", (), 1.008, "u"),
        _c("m_He", (), 4.002602, "u"),
        _c("m_Li", (), 6.94, "u"),
        _c("m_Be", (), 9.0121831, "u"),
        _c("m_B", (), 10.81, "u"),
        _c("m_C", (), 12.011, "u"),
        _c("m_N", (), 14.007, "u"),
        _c("m_O", (), 15.999, "u"),
        _c("m_F", (), 18.998403163, "u"),
        _c("m_Ne", (), 20.1797, "u"),
        _c("m_Na", (), 22.98976928, "u"),
        _c("m_Mg", (), 24.305, "u"),
        _c("m_Al", (), 26.9815385, "u"),
        _c("m_Si", (), 28.085, "u"),
        _c("m_P", (), 30.973761998, "u"),
        _c("m_S", (), 32.06, "u"),
        _c("m_Cl", (), 35.45, "u"),
        _c("m_Ar", (), 39.948, "u"),
        _c("m_K", (), 39.0983, "u"),
        _c("m_Ca", (), 40.078, "u"),
        _c("m_Sc", (), 44.955908, "u"),
        _c("m_Ti", (), 47.867, "u"),
        _c("m_V", (), 50.9415, "u"),
        _c("m_Cr", (), 51.9961, "u"),
        _c("m_Mn", (), 54.938044, "u"),
        _c("m_Fe", (), 55.845, "u"),
        _c("m_Co", (), 58.933194, "u"),
        _c("m_Ni", (), 58.6934, "u"),
        _c("m_Cu", (), 63.546, "u"),
        _c("m_Zn", (), 65.38, "u"),
        _c("m_Ga", (), 69.723, "u"),
        _c("m_Ge", (), 72.630, "u"),
        _c("m_As", (), 74.921595, "u"),
        _c("m_Se", (), 78.971, "u"),
        _c("m_Br", (), 79.904, "u"),
        _c("m_Kr", (), 83.798, "u"),
        _c("m_Rb", (), 85.4678, "u"),
        _c("m_Sr", (), 87.62, "u"),
        _c("m_Y", (), 88.90584, "u"),
        _c("m_Zr", (), 91.224, "u"),
        _c("m_Nb", (), 92.90637, "u"),
        _c("m_Mo", (), 95.95, "u"),
        _c("m_Ru", (), 101.07, "u"),
        _c("m_Rh", (), 102.90550, "u"),
        _c("m_Pd", (), 106.42, "u"),
        _c("m_Ag", (), 107.8682, "u"),
        _c("m_Cd", (), 112.414, "u"),
        _c("m_In", (), 114.818, "u"),
        _c("m_Sn", (), 118.710, "u"),
        _c("m_Sb", (), 121.760, "u"),
        _c("m_Te", (), 127.60, "u"),
        _c("m_I", (), 126.90447, "u"),
        _c("m_Xe", (), 131.293, "u"),
        _c("m_Cs", (), 132.90545196, "u"),
        _c("m_Ba", (), 137.327, "u"),
        _c("m_La", (), 138.90547, "u"),
        _c("m_Ce", (), 140.116, "u"),
        _c("m_Pr", (), 140.90766, "u"),
        _c("m_Nd", (), 144.242, "u"),
        _c("m_Sm", (), 150.36, "u"),
        _c("m_Eu", (), 151.964, "u"),
        _c("m_Gd", (), 157.25, "u"),
        _c("m_Tb", (), 158.92535, "u"),
        _c("m_Dy", (), 162.500, "u"),
        _c("m_Ho", (), 164.93033, "u"),
        _c("m_Er", (), 167.259, "u"),
        _c("m_Tm", (), 168.93422, "u"),
        _c("m_Yb", (), 173.054, "u"),
        _c("m_Lu", (), 174.9668, "u"),
        _c("m_Hf", (), 178.49, "u"),
        _c("m_Ta", (), 180.94788, "u"),
        _c("m_W", (), 183.84, "u"),
        _c("m_Re", (), 186.207, "u"),
        _c("m_Os", (), 190.23, "u"),
        _c("m_Ir", (), 192.217, "u"),
        _c("m_Pt", (), 195.084, "u"),
        _c("m_Au", (), 196.966569, "u"),
        _c("m_Hg", (), 200.592, "u"),
        _c("m_Tl", (), 204.38, "u"),
        _c("m_Pb", (), 207.2, "u"),
        _c("m_Bi", (), 208.98040, "u"), # no stable isotopes
        _c("m_Th", (), 232.0377, "u"),  # no stable isotopes
        _c("m_Pa", (), 231.03588, "u"), # no stable isotopes
        _c("m_U", (), 238.02891, "u"),  # no stable isotopes

        # Isotope masses.
        # http://www.ciaaw.org/atomic-masses.htm (IUPAC)
        #
        # They take their data from Wang et al., Chinese Physics C 36,
        # 1603 (2012), but I don't have access to this.
        #
        # TODO: sympy floats                                   
        # TODO: double-check                                   
        _c("m_H1", (), 1.0078250322, "u"),
        _c("m_H2", (), 2.0141017781, "u"),
        _c("m_He3", (), 3.01602932, "u"),
        _c("m_He4", (), 4.0026032541, "u"),
        _c("m_Li6", (), 6.015122887, "u"),
        _c("m_Li7", (), 7.01600344, "u"),
        _c("m_Be9", (), 9.0121831, "u"),
        _c("m_B10", (), 10.012937, "u"),
        _c("m_B11", (), 11.009305, "u"),
        _c("m_C12", (), 12, "u"),
        _c("m_C13", (), 13.003354835, "u"),
        _c("m_N14", (), 14.003074004, "u"),
        _c("m_N15", (), 15.000108899, "u"),
        _c("m_O16", (), 15.994914620, "u"),
        _c("m_O17", (), 16.999131757, "u"),
        _c("m_O18", (), 17.999159613, "u"),
        _c("m_F19", (), 18.998403163, "u"),
        _c("m_Ne20", (), 19.99244018, "u"),
        _c("m_Ne21", (), 20.9938467, "u"),
        _c("m_Ne22", (), 21.9913851, "u"),
        _c("m_Na23", (), 22.98976928, "u"),
        _c("m_Mg24", (), 23.98504170, "u"),
        _c("m_Mg25", (), 24.9858370, "u"),
        _c("m_Mg26", (), 25.9825930, "u"),
        _c("m_Al27", (), 26.9815385, "u"),
        _c("m_Si28", (), 27.976926535, "u"),
        _c("m_Si29", (), 28.976494665, "u"),
        _c("m_Si30", (), 29.97377001, "u"),
        _c("m_P31", (), 30.973761998, "u"),
        _c("m_S32", (), 31.972071174, "u"),
        _c("m_S33", (), 32.971458910, "u"),
        _c("m_S34", (), 33.9678670, "u"),
        _c("m_S36", (), 35.967081, "u"),
        _c("m_Cl35", (), 34.9688527, "u"),
        _c("m_Cl37", (), 36.9659026, "u"),
        _c("m_Ar36", (), 35.9675451, "u"),
        _c("m_Ar38", (), 37.962732, "u"),
        _c("m_Ar40", (), 39.96238312, "u"),
        _c("m_K39", (), 38.96370649, "u"),
        _c("m_K40", (), 39.9639982, "u"),
        _c("m_K41", (), 40.96182526, "u"),
        _c("m_Ca40", (), 39.9625909, "u"),
        _c("m_Ca42", (), 41.958618, "u"),
        _c("m_Ca43", (), 42.958766, "u"),
        _c("m_Ca44", (), 43.955482, "u"),
        _c("m_Ca46", (), 45.95369, "u"),
        _c("m_Ca48", (), 47.9525228, "u"),
        _c("m_Sc45", (), 44.955908, "u"),
        _c("m_Ti46", (), 45.952628, "u"),
        _c("m_Ti47", (), 46.951759, "u"),
        _c("m_Ti48", (), 47.947942, "u"),
        _c("m_Ti49", (), 48.947866, "u"),
        _c("m_Ti50", (), 49.944787, "u"),
        _c("m_V50", (), 49.947156, "u"),
        _c("m_V51", (), 50.943957, "u"),
        _c("m_Cr50", (), 49.946042, "u"),
        _c("m_Cr52", (), 51.940506, "u"),
        _c("m_Cr53", (), 52.940648, "u"),
        _c("m_Cr54", (), 53.938879, "u"),
        _c("m_Mn55", (), 54.938044, "u"),
        _c("m_Fe54", (), 53.939609, "u"),
        _c("m_Fe56", (), 55.934936, "u"),
        _c("m_Fe57", (), 56.935393, "u"),
        _c("m_Fe58", (), 57.933274, "u"),
        _c("m_Co59", (), 58.933194, "u"),
        _c("m_Ni58", (), 57.935342, "u"),
        _c("m_Ni60", (), 59.930786, "u"),
        _c("m_Ni61", (), 60.931056, "u"),
        _c("m_Ni62", (), 61.928345, "u"),
        _c("m_Ni64", (), 63.927967, "u"),
        _c("m_Cu63", (), 62.929598, "u"),
        _c("m_Cu65", (), 64.927790, "u"),
        _c("m_Zn64", (), 63.929142, "u"),
        _c("m_Zn66", (), 65.926034, "u"),
        _c("m_Zn67", (), 66.927128, "u"),
        _c("m_Zn68", (), 67.924845, "u"),
        _c("m_Zn70", (), 69.92532, "u"),
        _c("m_Ga69", (), 68.925574, "u"),
        _c("m_Ga71", (), 70.924703, "u"),
        _c("m_Ge70", (), 69.924249, "u"),
        _c("m_Ge72", (), 71.9220758, "u"),
        _c("m_Ge73", (), 72.9234590, "u"),
        _c("m_Ge74", (), 73.92117776, "u"),
        _c("m_Ge76", (), 75.9214027, "u"),
        _c("m_As75", (), 74.921595, "u"),
        _c("m_Se74", (), 73.9224759, "u"),
        _c("m_Se76", (), 75.9192137, "u"),
        _c("m_Se77", (), 76.9199142, "u"),
        _c("m_Se78", (), 77.917309, "u"),
        _c("m_Se80", (), 79.916522, "u"),
        _c("m_Se82", (), 81.916700, "u"),
        _c("m_Br79", (), 78.918338, "u"),
        _c("m_Br81", (), 80.916290, "u"),
        _c("m_Kr78", (), 77.920365, "u"),
        _c("m_Kr80", (), 79.916378, "u"),
        _c("m_Kr82", (), 81.913483, "u"),
        _c("m_Kr83", (), 82.914127, "u"),
        _c("m_Kr84", (), 83.91149773, "u"),
        _c("m_Kr86", (), 85.91061063, "u"),
        _c("m_Rb85", (), 84.91178974, "u"),
        _c("m_Rb87", (), 86.90918053, "u"),
        _c("m_Sr84", (), 83.913419, "u"),
        _c("m_Sr86", (), 85.909261, "u"),
        _c("m_Sr87", (), 86.908878, "u"),
        _c("m_Sr88", (), 87.905613, "u"),
        _c("m_Y89", (), 88.90584, "u"),
        _c("m_Zr90", (), 89.90470, "u"),
        _c("m_Zr91", (), 90.90564, "u"),
        _c("m_Zr92", (), 91.90503, "u"),
        _c("m_Zr94", (), 93.90631, "u"),
        _c("m_Zr96", (), 95.90827, "u"),
        _c("m_Nb93", (), 92.90637, "u"),
        _c("m_Mo92", (), 91.906808, "u"),
        _c("m_Mo94", (), 93.905085, "u"),
        _c("m_Mo95", (), 94.905839, "u"),
        _c("m_Mo96", (), 95.904676, "u"),
        _c("m_Mo97", (), 96.906018, "u"),
        _c("m_Mo98", (), 97.905405, "u"),
        _c("m_Mo100", (), 99.907472, "u"),
        _c("m_Tc98", (), 97.90721, "u"),
        _c("m_Ru96", (), 95.907590, "u"),
        _c("m_Ru98", (), 97.90529, "u"),
        _c("m_Ru99", (), 98.905934, "u"),
        _c("m_Ru100", (), 99.904214, "u"),
        _c("m_Ru101", (), 100.905577, "u"),
        _c("m_Ru102", (), 101.904344, "u"),
        _c("m_Ru104", (), 103.90543, "u"),
        _c("m_Rh103", (), 102.90550, "u"),
        _c("m_Pd102", (), 101.90560, "u"),
        _c("m_Pd104", (), 103.904031, "u"),
        _c("m_Pd105", (), 104.905080, "u"),
        _c("m_Pd106", (), 105.903480, "u"),
        _c("m_Pd108", (), 107.903892, "u"),
        _c("m_Pd110", (), 109.905172, "u"),
        _c("m_Ag107", (), 106.90509, "u"),
        _c("m_Ag109", (), 108.904755, "u"),
        _c("m_Cd106", (), 105.906460, "u"),
        _c("m_Cd108", (), 107.904183, "u"),
        _c("m_Cd110", (), 109.903007, "u"),
        _c("m_Cd111", (), 110.904183, "u"),
        _c("m_Cd112", (), 111.902763, "u"),
        _c("m_Cd113", (), 112.904408, "u"),
        _c("m_Cd114", (), 113.903365, "u"),
        _c("m_Cd116", (), 115.904763, "u"),
        _c("m_In113", (), 112.904062, "u"),
        _c("m_In115", (), 114.90387878, "u"),
        _c("m_Sn112", (), 111.904824, "u"),
        _c("m_Sn114", (), 113.902783, "u"),
        _c("m_Sn115", (), 114.9033447, "u"),
        _c("m_Sn116", (), 115.901743, "u"),
        _c("m_Sn117", (), 116.902954, "u"),
        _c("m_Sn118", (), 117.901607, "u"),
        _c("m_Sn119", (), 118.903311, "u"),
        _c("m_Sn120", (), 119.902202, "u"),
        _c("m_Sn122", (), 121.90344, "u"),
        _c("m_Sn124", (), 123.905277, "u"),
        _c("m_Sb121", (), 120.90381, "u"),
        _c("m_Sb123", (), 122.90421, "u"),
        _c("m_Te120", (), 119.90406, "u"),
        _c("m_Te122", (), 121.90304, "u"),
        _c("m_Te123", (), 122.90427, "u"),
        _c("m_Te124", (), 123.90282, "u"),
        _c("m_Te125", (), 124.90443, "u"),
        _c("m_Te126", (), 125.90331, "u"),
        _c("m_Te128", (), 127.904461, "u"),
        _c("m_Te130", (), 129.90622275, "u"),
        _c("m_I127", (), 126.90447, "u"),
        _c("m_Xe124", (), 123.90589, "u"),
        _c("m_Xe126", (), 125.90430, "u"),
        _c("m_Xe128", (), 127.903531, "u"),
        _c("m_Xe129", (), 128.90478086, "u"),
        _c("m_Xe130", (), 129.9035094, "u"),
        _c("m_Xe131", (), 130.905084, "u"),
        _c("m_Xe132", (), 131.90415509, "u"),
        _c("m_Xe134", (), 133.905395, "u"),
        _c("m_Xe136", (), 135.90721448, "u"),
        _c("m_Cs133", (), 132.90545196, "u"),
        _c("m_Ba130", (), 129.90632, "u"),
        _c("m_Ba132", (), 131.905061, "u"),
        _c("m_Ba134", (), 133.904508, "u"),
        _c("m_Ba135", (), 134.905688, "u"),
        _c("m_Ba136", (), 135.904576, "u"),
        _c("m_Ba137", (), 136.905827, "u"),
        _c("m_Ba138", (), 137.905247, "u"),
        _c("m_La138", (), 137.90712, "u"),
        _c("m_La139", (), 138.90636, "u"),
        _c("m_Ce136", (), 135.907129, "u"),
        _c("m_Ce138", (), 137.90599, "u"),
        _c("m_Ce140", (), 139.90544, "u"),
        _c("m_Ce142", (), 141.90925, "u"),
        _c("m_Pr141", (), 140.90766, "u"),
        _c("m_Nd142", (), 141.90773, "u"),
        _c("m_Nd143", (), 142.90982, "u"),
        _c("m_Nd144", (), 143.91009, "u"),
        _c("m_Nd145", (), 144.91258, "u"),
        _c("m_Nd146", (), 145.91312, "u"),
        _c("m_Nd148", (), 147.91690, "u"),
        _c("m_Nd150", (), 149.92090, "u"),
        _c("m_Pm145", (), 144.91276, "u"),
        _c("m_Sm144", (), 143.91201, "u"),
        _c("m_Sm147", (), 146.91490, "u"),
        _c("m_Sm148", (), 147.91483, "u"),
        _c("m_Sm149", (), 148.91719, "u"),
        _c("m_Sm150", (), 149.91728, "u"),
        _c("m_Sm152", (), 151.91974, "u"),
        _c("m_Sm154", (), 153.92222, "u"),
        _c("m_Eu151", (), 150.91986, "u"),
        _c("m_Eu153", (), 152.92124, "u"),
        _c("m_Gd152", (), 151.91980, "u"),
        _c("m_Gd154", (), 153.92087, "u"),
        _c("m_Gd155", (), 154.92263, "u"),
        _c("m_Gd156", (), 155.92213, "u"),
        _c("m_Gd157", (), 156.92397, "u"),
        _c("m_Gd158", (), 157.92411, "u"),
        _c("m_Gd160", (), 159.92706, "u"),
        _c("m_Tb159", (), 158.92535, "u"),
        _c("m_Dy156", (), 155.92428, "u"),
        _c("m_Dy158", (), 157.92442, "u"),
        _c("m_Dy160", (), 159.92520, "u"),
        _c("m_Dy161", (), 160.92694, "u"),
        _c("m_Dy162", (), 161.92681, "u"),
        _c("m_Dy163", (), 162.92874, "u"),
        _c("m_Dy164", (), 163.92918, "u"),
        _c("m_Ho165", (), 164.93033, "u"),
        _c("m_Er162", (), 161.92879, "u"),
        _c("m_Er164", (), 163.92921, "u"),
        _c("m_Er166", (), 165.93030, "u"),
        _c("m_Er167", (), 166.93205, "u"),
        _c("m_Er168", (), 167.93238, "u"),
        _c("m_Er170", (), 169.93547, "u"),
        _c("m_Tm169", (), 168.93422, "u"),
        _c("m_Yb168", (), 167.93389, "u"),
        _c("m_Yb170", (), 169.93477, "u"),
        _c("m_Yb171", (), 170.93633, "u"),
        _c("m_Yb172", (), 171.93639, "u"),
        _c("m_Yb173", (), 172.93822, "u"),
        _c("m_Yb174", (), 173.93887, "u"),
        _c("m_Yb176", (), 175.94258, "u"),
        _c("m_Lu175", (), 174.94078, "u"),
        _c("m_Lu176", (), 175.94269, "u"),
        _c("m_Hf174", (), 173.94005, "u"),
        _c("m_Hf176", (), 175.94141, "u"),
        _c("m_Hf177", (), 176.94323, "u"),
        _c("m_Hf178", (), 177.94371, "u"),
        _c("m_Hf179", (), 178.94582, "u"),
        _c("m_Hf180", (), 179.94656, "u"),
        _c("m_Ta180", (), 179.94746, "u"),
        _c("m_Ta181", (), 180.94800, "u"),
        _c("m_W180", (), 179.94671, "u"),
        _c("m_W182", (), 181.948204, "u"),
        _c("m_W183", (), 182.950223, "u"),
        _c("m_W184", (), 183.950931, "u"),
        _c("m_W186", (), 185.95436, "u"),
        _c("m_Re185", (), 184.952955, "u"),
        _c("m_Re187", (), 186.95575, "u"),
        _c("m_Os184", (), 183.952489, "u"),
        _c("m_Os186", (), 185.95384, "u"),
        _c("m_Os187", (), 186.95575, "u"),
        _c("m_Os188", (), 187.95584, "u"),
        _c("m_Os189", (), 188.95814, "u"),
        _c("m_Os190", (), 189.95844, "u"),
        _c("m_Os192", (), 191.96148, "u"),
        _c("m_Ir191", (), 190.96059, "u"),
        _c("m_Ir193", (), 192.96292, "u"),
        _c("m_Pt190", (), 189.95993, "u"),
        _c("m_Pt192", (), 191.96104, "u"),
        _c("m_Pt194", (), 193.962681, "u"),
        _c("m_Pt195", (), 194.964792, "u"),
        _c("m_Pt196", (), 195.964952, "u"),
        _c("m_Pt198", (), 197.96789, "u"),
        _c("m_Au197", (), 196.966569, "u"),
        _c("m_Hg196", (), 195.96583, "u"),
        _c("m_Hg198", (), 197.966769, "u"),
        _c("m_Hg199", (), 198.968281, "u"),
        _c("m_Hg200", (), 199.968327, "u"),
        _c("m_Hg201", (), 200.970303, "u"),
        _c("m_Hg202", (), 201.970643, "u"),
        _c("m_Hg204", (), 203.973494, "u"),
        _c("m_Tl203", (), 202.972345, "u"),
        _c("m_Tl205", (), 204.974428, "u"),
        _c("m_Pb204", (), 203.973044, "u"),
        _c("m_Pb206", (), 205.974466, "u"),
        _c("m_Pb207", (), 206.975897, "u"),
        _c("m_Pb208", (), 207.976653, "u"),
        _c("m_Bi209", (), 208.98040, "u"),
        _c("m_Th230", (), 230.03313, "u"),
        _c("m_Th232", (), 232.03806, "u"),
        _c("m_Pa231", (), 231.03588, "u"),
        _c("m_U233", (), 233.03964, "u"),
        _c("m_U234", (), 234.04095, "u"),
        _c("m_U235", (), 235.04393, "u"),
        _c("m_U238", (), 238.05079, "u"),

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
