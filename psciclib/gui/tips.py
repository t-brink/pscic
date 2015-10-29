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

import random

# These tips will be randomly shown in the input field.
tips = ["Enter expression to calculate.",
        "You can use units, e.g. “1cm + 1in”.",
        "Convert units by appending “to <unit>”.",
        "Equalities like “1 = 0” will be checked for truth.",
        "Equalities like “x - 1 = 0” will be solved for x.",
        "Expressions like “x^2 + 4” will be plotted.",

        # Uncommon tips.
        "Prefix roman numerals with 0r: “0rIV” → 4.",
        "Input binary numbers: 0b10011.",
        "Input octal numbers: 0o755.",
        "Input hexadecimal numbers: 0xFF.",
        ]


def get_a_tip():
    # TODO: on first use, show them in order.    
    return random.choice(tips)
