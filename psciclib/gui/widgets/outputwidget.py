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

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtWidgets
import pyparsing

from ... import operators
from ... import exceptions
from ... import units

class OutputWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # The output QLabel.
        self.output_field = QtWidgets.QLabel(parent=self)
        self.output_field.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self.output_field.setAlignment(Qt.AlignRight | Qt.AlignTop)

        # Layout.
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.output_field)
        self.output_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)

        self.setLayout(layout)

    def update_output(self, val):
        style = ""
        text = ""
        if isinstance(val, (exceptions.Error, pyparsing.ParseException)):
            style = "color: red;"
            text = "Parsing error: " + str(val)
        elif isinstance(val, ValueError):
            style = "color: red;"
            text = "Value error: " + str(val)
        else:
            # Correct output.
            style = "font-size: x-large;"
            if isinstance(val, units.Q_):
                # pretty-print units.
                text = "= {:H~}".format(val)
            elif isinstance(val, operators.Equality.Solutions):
                text = "<br>".join(
                    "<i>{!s}</i> = {}".format(
                        val.x,
                        ("{:H~}".format(sol)
                         if isinstance(sol, units.Q_) # TODO: repeated code here
                         else "{!s}".format(sol))
                    )
                    for sol in val.solutions
                )
            elif isinstance(val, bool):
                text = str(val)
            else:
                text = "= {!s}".format(val)
        self.output_field.setText('<span style="{}">'.format(style)
                                  + text
                                  + '</span>')
