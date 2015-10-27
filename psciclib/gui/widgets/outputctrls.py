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

class OutputCtrls(QtWidgets.QWidget):

    # exact, float_display
    changed = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.output_label = QtWidgets.QLabel("Output:")

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

        # Set layout.
        layout = QtWidgets.QHBoxLayout()

        layout.addWidget(self.output_label)
        self.output_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                        QtWidgets.QSizePolicy.Fixed)

        layout.addWidget(self.exact_or_float)

        layout.addWidget(self.float_display)

        self.setLayout(layout)

    def emit_changed(self):
        self.changed.emit(*self.data)

    @property
    def data(self):
        return (self.exact_or_float.isChecked(),
                self.float_display.currentData())

