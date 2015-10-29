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

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWebKitWidgets import QWebView

from .. import version

class HelpWindow(QtWidgets.QWidget):

    # TODO: do not hardcode this path like this.
    __doc_path = os.path.abspath(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..", "..", "doc", "index.html"))

    def __init__(self, parent=None):
        super().__init__(parent)

        # The help display.
        self.help_display = QWebView(parent=self)
        self.help_display.load(QtCore.QUrl("file://" + self.__doc_path))

        # Close button.
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        # Layout for the widgets.
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.help_display)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        # Title
        self.setWindowTitle("{} help".format(version.progname))


