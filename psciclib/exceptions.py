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

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class UnknownFunctionError(Error):
    """Function name unknown."""
    def __init__(self, funcname):
        self.funcname = funcname

    def __str__(self):
        return "Unknown function: {!s}".format(self.funcname)

    def __repr__(self):
        return "UnknownFunctionError({!r})".format(self.funcname)


class UnknownConstantError(Error):
    """Unknown constant or variable name."""
    def __init__(self, constname):
        self.constname = constname

    def __str__(self):
        return "Unknown constant or variable: {!s}".format(self.constname)

    def __repr__(self):
        return "UnknownConstantError({!r})".format(self.constname)


class UnknownUnitError(Error):
    """Unknown unit name."""
    def __init__(self, unitname):
        self.unitname = unitname

    def __str__(self):
        return "Unknown unit: {!s}".format(self.unitname)

    def __repr__(self):
        return "UnknownUnitError({!r})".format(self.unitname)


class WrongNumberOfArgumentsError(Error):
    """Wrong number of arguments for function."""
    def __init__(self, funcname, n_args, min_args, max_args):
        self.funcname = funcname
        self.n_args = n_args
        self.min_args = min_args
        self.max_args = max_args

    def __str__(self):
        if self.min_args == self.max_args:
            return "Function {} takes {} arguments, not {}.".format(
                self.funcname, self.min_args, self.n_args
            )
        elif self.n_args < self.min_args:
            return "Function {} takes at least {} arguments, {} given.".format(
                self.funcname, self.min_args, self.n_args
            )
        else:
            return "Function {} takes at most {} arguments, {} given.".format(
                self.funcname, self.max_args, self.n_args
            )

    __repr__ = __str__


class VariableLengthRowsError(Error):
    """Matrix has rows of different length."""
    pass


