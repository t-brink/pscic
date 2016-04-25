#!/usr/bin/env python3

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


# extract data from the table from http://www.ciaaw.org/atomic-masses.htm
# worked on 2016-04-25, no guarantee for later.

from bs4 import BeautifulSoup

with open("isotope_masses.table.html") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

table = soup.body.table

template = '        _c("m_{}{}", (), {}, "u"),'

cur_elem = None
for i, row in enumerate(table.find_all("tr")):
    cells = row.find_all("td")
    l = len(cells)
    if l == 5:
        cur_elem = cells[1].text.strip()
        num_idx = 3
        mass_idx = 4
    elif l == 2:
        num_idx = 0
        mass_idx = 1
    else:
        # some trash data.
        continue
    iso_num = int(cells[num_idx].text.strip().strip("*").strip())
    mass = cells[mass_idx].text.strip().split("(")[0].strip()
    mass = "".join(mass.split()) # remove all spaces
    assert cur_elem is not None
    print(template.format(cur_elem, iso_num, mass))


