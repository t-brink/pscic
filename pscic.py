#!/usr/bin/env python3

# Copyright (C) 2015, 2016  Tobias Brink
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

import pyparsing

from psciclib import parseexpr
from psciclib.exceptions import Error
from psciclib.units import Q_
from psciclib import unitbridge
from psciclib.result import Mode

while True:
    try:
        expr = input("> ")
    except EOFError:
        print()
        break
    try:
        tree = parseexpr.parse(expr)
    except (Error, pyparsing.ParseException) as e:
        print(e)
        continue
    print(tree)
    try:
        val = tree.evaluate()
    except ValueError as e:
        print("ValueError:", e)
        continue
    # Solve numerically if needed. TODO: some way for the user to provide x0 
    if val.is_unsolved:
        val_ = val.nsolve(1.0) # TODO: x0 from user 
        if val_ is not None:
            # We found a numerical solution.
            val = val_
        del val_
    # TODO: make format options available somehow
    print(val.as_string())
