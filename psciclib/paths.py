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

import os
import errno

import appdirs

CACHE_DIR = appdirs.user_cache_dir(appname="pscic",
                                   appauthor="TobiasBrink",
                                   opinion=True)


def make_paths():
    """Make sure all paths exist."""
    try:
        os.makedirs(CACHE_DIR)
    except FileExistsError:
        # Already exists.
        pass


#TODO: put into some sort of init that is called centrally
make_paths()