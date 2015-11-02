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

from ... import result
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
        self.output_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)

        self.output_scrollarea = QtWidgets.QScrollArea()
        self.output_scrollarea.setWidget(self.output_field)
        self.output_scrollarea.setWidgetResizable(True)
        self.output_scrollarea.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )
        self.output_scrollarea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )
        self.output_scrollarea.setAlignment(Qt.AlignRight | Qt.AlignTop)
        # Make it invisible
        self.output_scrollarea.setFrameStyle(QtWidgets.QFrame.NoFrame)

        # Layout.
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.output_scrollarea)

        self.setLayout(layout)

    def update_output(self, val, mode, numeral_system, digits, units):
        style = ""
        text = ""
        if isinstance(val, (exceptions.Error, pyparsing.ParseException)):
            style = "color: red;"
            text = "Parsing error: " + str(val)
        elif isinstance(val, ValueError):
            style = "color: red;"
            text = "Value error: " + str(val)
        elif val is None:
            # No input string, so show no result.
            style = ""
            text = ""
        else:
            # Correct output.
            style = "font-size: x-large;"
            try:
                text = val.as_string(mode, numeral_system, digits, units)
            except ValueError as e:
                style = "color: red;"
                text = "Printing error: " + str(e)
            else:
                # TODO: this is a hack, we should actually use a   
                # pretty-printer which outputs some sort of markup 
                # (html or mathml) to put that into a widget which 
                # understands it. Still, I want newlines for now.  
                text = text.replace("\n", "<br>")
        self.output_field.setText('<span style="{}">'.format(style)
                                  + text
                                  + '</span>')
