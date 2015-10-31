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

import pint

from . import currency

# Default init.
ureg = pint.UnitRegistry()
ureg.default_format = "~" # print abbreviations by default.
Q_ = ureg.Quantity
UndefinedUnitError = pint.UndefinedUnitError

def _init():
    # Add currencies to registry.
    # TODO: make the download thing optional! ship default .xml!
    # TODO: error handling
    data = currency.get_exchange_rates()
    ureg.define("EUR = [currency]")
    for cur, rate in data["rates"].items():
        ureg.define("{} = {} * EUR".format(cur, 1/rate))

