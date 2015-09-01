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

from xml.etree import ElementTree
import urllib.request
import re
import datetime
import os

from . import paths

CURRENCY_CRE = re.compile(r'[A-Z]{3}')

def parse(string):
    """Parse ECB's currency conversion rates.

    May raise:

    xml.etree.ElementTree.ParseError
    ValueError

    """
    root = ElementTree.fromstring(string)
    # Convert to dictionary, so that it can be stored as JSON.
    cubes = root.findall("{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube")
    if len(cubes) != 1:
        raise ValueError("Outer 'Cube' element not found or duplicate!")
    cube_outer = cubes[0]
    cubes = cube_outer.findall("{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube")
    if len(cubes) != 1:
        raise ValueError("Inner 'Cube' element not found or duplicate!")
    cube = cubes[0]
    # Get date.
    date = datetime.datetime.strptime(cube.attrib["time"], "%Y-%m-%d").date()
    # Get exchange rates.
    rates = {} # EUR is 1.0 always.
    for child in cube:
        currency = child.attrib["currency"]
        if not CURRENCY_CRE.fullmatch(currency):
            raise ValueError("Invalid currency code: {}".format(currency))
        rate = float(child.attrib["rate"])
        if currency in rates:
            raise ValueError("Duplicate currency: {}".format(currency))
        elif currency == "EUR":
            raise ValueError("EUR must not be in input xml but is.")
        rates[currency] = rate
    return {"date": date, "rates": rates}


def get_exchange_rates():
    # Uses ECB.
    the_url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    data = None
    # Try to read from cache.
    cached_file = os.path.join(paths.CACHE_DIR, "eurofxref-daily.xml")
    try:
        with open(cached_file) as f:
            string = f.read()
    except FileNotFoundError:
        # File does not exists.
        pass
    else:
        # File does exists, try to parse.
        try:
            data = parse(string)
        except (ElementTree.ParseError, ValueError):
            # Failed to parse.
            data = None
    # See how old the cache is if it exists. If older than 2 days, reload.
    if (data is None
        or
        datetime.datetime.now().date() - data["date"] > datetime.timedelta(days=2)):
        # Too old or does not exist.
        with urllib.request.urlopen(the_url) as response:
            string = response.read()
        data = parse(string)
        # Write cache.
        with open(cached_file, "wb") as f:
            f.write(string)
        #TODO: on any error before here, return the cached data and warn the user!
        return data
    else:
        return data
