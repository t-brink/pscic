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


class QuickButtons(QtWidgets.QWidget):

    base_units_clicked = pyqtSignal()
    best_units_clicked = pyqtSignal()
    copy_paste_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # TODO: icons! 
        self.base_units_btn = QtWidgets.QToolButton(parent=self)
        self.base_units_btn.setText("base")
        self.base_units_btn.setToolTip("Convert result to SI base units.")
        self.base_units_btn.clicked.connect(self.base_units_clicked)

        self.best_units_btn = QtWidgets.QToolButton(parent=self)
        self.best_units_btn.setText("best")
        self.best_units_btn.setToolTip("Convert result to shortest SI units.")
        self.best_units_btn.clicked.connect(self.best_units_clicked)

        self.copy_paste_btn = QtWidgets.QToolButton(parent=self)
        self.copy_paste_btn.setText("C/P")
        self.copy_paste_btn.setToolTip("Convert results to computer-readable "
                                       "plain text, ready for copy-pasting.")
        self.copy_paste_btn.clicked.connect(self.copy_paste_clicked)

        # Set layout.
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.base_units_btn)
        self.base_units_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                          QtWidgets.QSizePolicy.Fixed)

        layout.addWidget(self.best_units_btn)
        self.best_units_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                          QtWidgets.QSizePolicy.Fixed)

        layout.addWidget(self.copy_paste_btn)
        self.copy_paste_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                          QtWidgets.QSizePolicy.Fixed)

        layout.addStretch()

        self.setLayout(layout)