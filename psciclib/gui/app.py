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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
import pyparsing

from .. import parseexpr
from ..exceptions import Error
from ..units import Q_


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.input_field = QtWidgets.QLineEdit()

        self.parsed_field = QtWidgets.QLabel()
        self.parsed_field.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self.output_field = QtWidgets.QLabel()
        self.output_field.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self.input_field.returnPressed.connect(self.calculate)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.parsed_field)
        layout.addWidget(self.output_field)

        self.setLayout(layout)
        self.setWindowTitle("pscic")

    def calculate(self):
        expr = self.input_field.text()
        self.input_field.setText("")

        # Parse.
        try:
            tree = parseexpr.parse(expr)
        except (Error, pyparsing.ParseException) as e:
            self.parsed_field.setText("")
            self.output_field.setText(
                r'<span style="color:red;">{!s}</span>'.format(e)
            )
            return
        self.parsed_field.setText(
            r'<span style="color:gray;">{!s}</span>'.format(tree)
        )
        # Evaluate.
        try:
            val = tree.evaluate()
        except ValueError as e:
            self.output_field.setText(
                r'<span style="color:red;">ValueError: {!s}</span>'.format(e)
            )
            return
        # Output.
        if isinstance(val, Q_):
            # pretty-print units.
            val = "{:H~}".format(val)
        else:
            val = "{!s}".format(val)
        self.output_field.setText(val)


def main(argv):
    app = QtWidgets.QApplication(argv)

    main_window = MainWindow()
    main_window.show()

    return app.exec_()
