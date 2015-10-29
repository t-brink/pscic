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

from ... import version

class StatusBar:

    def __init__(self, status_bar, parent=None):
        self.status_bar = status_bar
        # Version display. TODO: Do we want that?
        self.permanent_msg = QtWidgets.QLabel("v" + version.version)
        self.status_bar.addPermanentWidget(self.permanent_msg)
        # Normal status display.
        self.status_msg = QtWidgets.QLabel(
            "Welcome to {}!".format(version.progname)
        )
        self.status_bar.addWidget(self.status_msg)

    def set_msg(self, text):
        self.status_msg.setText(text)

    def set_tmp(self, text, timeout=1000):
        """Temporary status bar message."""
        self.status_bar.showMessage('=> ' + text + ' <=', timeout)

    def set_walltime(self, time):
        if time < 0.001:
            s = "{:.2e}".format(time)
            pre,post = s.split("e", 1)
            pre.rstrip("0").rstrip(".")
            s = pre + "e" + post + " s"
        else:
            s = "{:.3g} s".format(time)
        self.status_msg.setText("calc: " + s)
