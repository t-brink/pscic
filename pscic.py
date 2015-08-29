#!/usr/bin/env python3

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

try:
    import readline
except ImportError:
    pass

from psciclib import parseexpr
from psciclib.exceptions import Error
from psciclib.units import Q_

while True:
    try:
        expr = input("> ")
    except EOFError:
        print()
        break
    try:
        tree = parseexpr.parse(expr)
    except Error as e:
        print(e)
        continue
    print(tree)
    try:
        val = tree.evaluate()
    except ValueError as e:
        print("ValueError:", e)
        continue
    if isinstance(val, Q_):
        # pretty-print units.
        val = "{:P~}".format(val)
    print("=", val)
