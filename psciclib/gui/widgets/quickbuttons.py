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

import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


class QuickButtons(QtWidgets.QWidget):

    input_size_toggled = pyqtSignal()
    base_units_clicked = pyqtSignal()
    best_units_clicked = pyqtSignal()
    copy_paste_clicked = pyqtSignal()

    # Icons.
    __incr_input_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     os.path.pardir,
                                     "icons", "adwaita-icon-theme-3.18.0",
                                     "incr-input-size.svg")
    __decr_input_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     os.path.pardir,
                                     "icons", "adwaita-icon-theme-3.18.0",
                                     "decr-input-size.svg")
    __base_units_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     os.path.pardir,
                                     "icons", "adwaita-icon-theme-3.18.0",
                                     "base-units.svg")
    __best_units_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     os.path.pardir,
                                     "icons", "adwaita-icon-theme-3.18.0",
                                     "best-units.svg")
    __copy_paste_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     os.path.pardir,
                                     "icons", "adwaita-icon-theme-3.18.0",
                                     "copy-paste-mode.svg")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.input_size_btn = QtWidgets.QToolButton(parent=self)
        self.input_size_btn.setIconSize(QtCore.QSize(24,24))
        self.input_size_btn.setToolTip("Toggle multi-line input.")
        self.input_size_btn.clicked.connect(self.input_size_toggled)
        self._input_size_icon_incr = QtGui.QIcon(self.__incr_input_icon)
        self._input_size_icon_decr = QtGui.QIcon(self.__decr_input_icon)

        self.base_units_btn = QtWidgets.QToolButton(parent=self)
        self.base_units_btn.setIcon(QtGui.QIcon(self.__base_units_icon))
        self.base_units_btn.setIconSize(QtCore.QSize(24,24))
        self.base_units_btn.setToolTip("Convert result to SI base units.")
        self.base_units_btn.clicked.connect(self.base_units_clicked)

        self.best_units_btn = QtWidgets.QToolButton(parent=self)
        self.best_units_btn.setIcon(QtGui.QIcon(self.__best_units_icon))
        self.best_units_btn.setIconSize(QtCore.QSize(24,24))
        self.best_units_btn.setToolTip("Convert result to shortest SI units.")
        self.best_units_btn.clicked.connect(self.best_units_clicked)

        self.copy_paste_btn = QtWidgets.QToolButton(parent=self)
        self.copy_paste_btn.setIcon(QtGui.QIcon(self.__copy_paste_icon))
        self.copy_paste_btn.setIconSize(QtCore.QSize(24,24))
        self.copy_paste_btn.setToolTip("Convert results to computer-readable "
                                       "plain text, ready for copy-pasting.")
        self.copy_paste_btn.clicked.connect(self.copy_paste_clicked)

        # Set layout.
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.input_size_btn)
        self.input_size_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                          QtWidgets.QSizePolicy.Fixed)

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

    def set_input_toggle_btn(self, multiline):
        self.input_size_btn.setIcon(
            self._input_size_icon_decr
            if multiline
            else self._input_size_icon_incr
        )
