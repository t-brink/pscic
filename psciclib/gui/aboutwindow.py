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
        self.authors = QtWidgets.QLabel("Authors:<br>Tobias Brink")

        # The license texts.
        self.license = QtWidgets.QLabel(
            "<p>Copyright (C) {}  {}<br>".format(version.copyright_years,
                                                 version.copyright_authors) +
            "This program is free software: you can redistribute it and/or "
            "modify it under the terms of the GNU General Public License as "
            "published by the Free Software Foundation, either version 3 of "
            "the License, or (at your option) any later version.</p>" +
            "<p>This program is distributed in the hope that it will be "
            "useful, "
            "but WITHOUT ANY WARRANTY; without even the implied warranty of "
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
            "GNU General Public License for more details.</p>" +
            "<p>You should have received a copy of the GNU General Public "
            "License "
            "along with this program.  If not, see "
            '&lt;<a href="http://www.gnu.org/licenses/">'
            'http://www.gnu.org/licenses/</a>&gt;.</p>' +
            "<hr>" +
            "<p>This program uses (modified) icons from the Adwaita icon set "
            'by the <a href="http://www.gnome.org">GNOME project</a>:</p>' +
            "<p>This work is licenced under the terms of either the GNU LGPL "
            "v3 or Creative Commons Attribution-Share Alike 3.0 United "
            "States License.</p>" +
            "<p>To view a copy of the CC-BY-SA licence, visit "
            '<a href="http://creativecommons.org/licenses/by-sa/3.0/">'
            'http://creativecommons.org/licenses/by-sa/3.0/</a> '
            "or send a letter to Creative Commons, 171 Second Street, "
            "Suite 300, San Francisco, California 94105, USA.</p>" +
            "<hr>" +
            '<p>This program uses <a href="http://www.sympy.org/">SymPy</a>:'
            '</p>' +
            "<p>Redistribution and use in source and binary forms, "
            "with or without "
            "modification, are permitted provided that the following "
            "conditions are met:</p>"+
            "<p>a. Redistributions of source code must retain the above "
            "copyright notice, this list of conditions and the following "
            "disclaimer.</p>"+
            "<p>b. Redistributions in binary form must reproduce the "
            "above copyright notice, this list of conditions and the "
            "following disclaimer in the documentation and/or other "
            "materials provided with the distribution.</p>" +
            "<p>c. Neither the name of SymPy nor the names of its "
            "contributors may be used to endorse or promote products "
            "derived from this software without specific prior "
            "written permission.</p>"+
            "<p>THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "
            'AND CONTRIBUTORS "AS IS"'
            "AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT "
            "LIMITED TO, "
            "THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR "
            "A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE "
            "REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, "
            "INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL "
            "DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF "
            "SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR "
            "PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON "
            "ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT "
            "LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) "
            "ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN "
            "IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.</p>"
            "<hr>" +
            '<p>This program uses '
            '<a href="http://pint.readthedocs.org/">Pint</a>:'
            '</p>' +
            '<p>Copyright (c) 2012 by Hernan E. Grecco and contributors.  See AUTHORS for more details.</p>'+
            '<p>Some rights reserved.</p>'+
            "<p>Redistribution and use in source and binary forms of the software as well as documentation, with or without modification, are permitted provided that the following conditions are met:</p>"+
            "<p>* Redistributions of source code must retain the above "
            "copyright notice, this list of conditions and the following "
            "disclaimer.</p>"+
            "<p>* Redistributions in binary form must reproduce the "
            "above copyright notice, this list of conditions and the "
            "following disclaimer in the documentation and/or other "
            "materials provided with the distribution.</p>" +
            "<p>* The names of the contributors may not be used to endorse or "
            "promote products derived from this software without specific "
            "prior written permission.</p>"+
            '<p>THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.</p>' +
            "<hr>" +
            '<p>This program uses <a href="http://pyparsing.wikispaces.com/">pyparsing</a>:</p>' +
            '<p>Copyright (c) 2003,2004  Paul T. McGuire</p>' +
            '<p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>'+
            '<p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>'+
            '<p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>'
            "<hr>" +
            '<p>This program uses <a href="https://pypi.python.org/pypi/appdirs/">appdirs</a>:</p>' +
            '<p> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>' +
            '<p> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>' +
            '<p> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>' +
            "<hr>" +
            'This program uses <a href="https://riverbankcomputing.com/software/pyqt/">PyQt5</a> which is licensed under the GPLv3, see above.</p>' +
            "<hr>" +
            'This program is written in <a href="http://python.org/">Python</a>.</p>'
        )
        self.license.setWordWrap(True)
        self.license.setOpenExternalLinks(True)
        self.license_scrollarea = QtWidgets.QScrollArea()
        self.license_scrollarea.setWidget(self.license)
        self.license_scrollarea.setWidgetResizable(True)
        self.license_scrollarea.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self.license_scrollarea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.license_scrollarea.setFrameStyle(QtWidgets.QFrame.NoFrame)

        # Close button.
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        # Layout for the widgets.
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layout1)
        layout.addWidget(self.authors)
        layout.addWidget(self.license_scrollarea)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        # Title
        self.setWindowTitle("About {}".format(version.progname))
