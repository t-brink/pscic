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

from ...result import NumeralSystem, Mode

class OutputCtrls(QtWidgets.QWidget):

    # exact, float_display
    changed = pyqtSignal(Mode, str, NumeralSystem, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.exact_or_float = QtWidgets.QToolButton(parent=self)
        self.exact_or_float.setText("Exact")
        self.exact_or_float.setCheckable(True)
        self.exact_or_float.setChecked(False)
        self.exact_or_float.toggled.connect(self.emit_changed)

        self.float_display = QtWidgets.QComboBox(parent=self)
        self.float_display.addItem("Normal", "norm")
        self.float_display.addItem("Engineering", "eng")
        self.float_display.addItem("Scientific", "sci")
        self.float_display.addItem("Simple", "simp")
        self.float_display.currentIndexChanged.connect(self.emit_changed)

        self.numeral_system = QtWidgets.QComboBox(parent=self)
        self.numeral_system.addItem("Binary", NumeralSystem.binary)
        self.numeral_system.addItem("Octal", NumeralSystem.octal)
        self.numeral_system.addItem("Decimal", NumeralSystem.decimal)
        self.numeral_system.addItem("Hexadecimal", NumeralSystem.hexadecimal)
        self.numeral_system.addItem("Roman numeral", NumeralSystem.roman)
        self.numeral_system.setCurrentIndex(2)
        self.numeral_system.currentIndexChanged.connect(self.emit_changed)

        self.precision_label = QtWidgets.QLabel("Precision:")

        self.precision_chooser = QtWidgets.QSpinBox(parent=self)
        self.precision_chooser.setMinimum(1)
        self.precision_chooser.setMaximum(99)
        self.precision_chooser.setValue(8)
        self.precision_chooser.valueChanged.connect(self.emit_changed)

        # Set layout.
        layout = QtWidgets.QHBoxLayout()

        layout.addWidget(self.exact_or_float)
        layout.addWidget(self.float_display)
        layout.addWidget(self.numeral_system)
        layout.addWidget(self.precision_label)

        self.precision_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(self.precision_chooser)

        self.setLayout(layout)

    def emit_changed(self):
        self.changed.emit(*self.data)

    @property
    def data(self):
        return ((Mode.try_exact
                 if self.exact_or_float.isChecked()
                 else Mode.to_float),
                self.float_display.currentData(),
                self.numeral_system.currentData(),
                self.precision_chooser.value())

