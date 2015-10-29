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

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

from .. import version

class AboutWindow(QtWidgets.QWidget):

    # TODO: do not hardcode this path like this.
    __icon_path = os.path.abspath(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "icons", "logo-path.svg"))

    def __init__(self, parent=None):
        super().__init__(parent)

        # The icon and title.
        icon_svg = QtSvg.QSvgRenderer(self.__icon_path)
        self.icon_image = QtGui.QImage(100,100, # TODO do no hardcode size?
                                       QtGui.QImage.Format_ARGB32_Premultiplied)
        self.icon_image.fill(QtCore.Qt.transparent);
        icon_painter = QtGui.QPainter(self.icon_image)
        icon_svg.render(icon_painter)
        self.icon_pixmap = QtGui.QPixmap()
        self.icon_pixmap.convertFromImage(self.icon_image)
        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(self.icon_pixmap)

        self.titletext = QtWidgets.QLabel(
            "{} version {}".format(version.progname, version.version)
        )

        layout1 = QtWidgets.QHBoxLayout()
        layout1.addWidget(self.icon)
        layout1.addWidget(self.titletext)

        # The authors. TODO: get list from soem file    
        self.authors = QtWidgets.QLabel("Authors:<br>Tobias Brink"
                                        "<br><br>"
                                        "(C) "
                                        "{}".format(version.copyright_years))

        # The license texts.
        self.license = QtWidgets.QLabel(
            "pscic under GPLv3<br>"
            "TODO: other licenses and full text of those")

        # Close button.
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        # Layout for the widgets.
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layout1)
        layout.addWidget(self.authors)
        layout.addWidget(self.license)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        # Title
        self.setWindowTitle("About {}".format(version.progname))


