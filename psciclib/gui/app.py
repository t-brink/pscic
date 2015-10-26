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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import pyparsing

from .. import parseexpr
from .. import operators
from ..exceptions import Error
from ..units import Q_
from .helpwindow import HelpWindow
from .aboutwindow import AboutWindow


# TODO:            
# * Put parts of the main window into separate custom widgets to reduce
#   clutter


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # The main input area. #########################################
        self.input_area = QtWidgets.QWidget(parent=self)

        # Widgets.
        self.input_field = QtWidgets.QLineEdit(parent=self.input_area)

        self.parsed_field = QtWidgets.QLabel(parent=self.input_area)
        self.parsed_field.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self.mode_field = QtWidgets.QLabel(parent=self.input_area)

        below_entry_layout = QtWidgets.QHBoxLayout()
        below_entry_layout.addWidget(self.parsed_field)
        self.parsed_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Fixed)
        below_entry_layout.addWidget(self.mode_field)
        self.mode_field.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Fixed)

        self.output_field = QtWidgets.QLabel(parent=self.input_area)
        self.output_field.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self.output_field.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self.input_field.returnPressed.connect(self.calculate)

        # Output controls.
        self.output_label = QtWidgets.QLabel("Output:")
        self.exact_or_float = QtWidgets.QToolButton(parent=self.input_area)
        self.exact_or_float.setText("Exact")
        self.exact_or_float.setCheckable(True)
        self.exact_or_float.setChecked(False)
        self.exact_or_float.toggled.connect(self.calculate)
        self.exact_or_float.toggled.connect(self.update_mode_field)
        # TODO: do not re-calculate, but change the output only     
        #       this needs support in the lower layers              

        self.float_display = QtWidgets.QComboBox(parent=self.input_area)
        self.float_display.addItem("Normal", "norm")
        self.float_display.addItem("Engineering", "eng")
        self.float_display.addItem("Scientific", "sci")
        self.float_display.addItem("Simple", "simp")
        self.float_display.currentIndexChanged.connect(self.calculate)
        # TODO: do not re-calculate, but change the output only     
        #       this needs support in the lower layers              

        output_ctrls_layout = QtWidgets.QHBoxLayout()
        output_ctrls_layout.addWidget(self.output_label)
        self.output_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                        QtWidgets.QSizePolicy.Fixed)
        output_ctrls_layout.addWidget(self.exact_or_float)
        output_ctrls_layout.addWidget(self.float_display)

        # Layout for the widgets.
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.input_field)
        self.input_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Fixed)
        layout.addLayout(below_entry_layout)
        layout.addWidget(self.output_field)
        self.output_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)
        layout.addLayout(output_ctrls_layout)

        # Assign the input area to the main window.
        self.input_area.setLayout(layout)
        self.setCentralWidget(self.input_area)

        # Menu bar. ####################################################
        menu_bar = self.menuBar()

        # Help menu.
        self.menu_help = menu_bar.addMenu("&Help")

        help_ = self.menu_help.addAction("&Help")
        help_.triggered.connect(self.show_help)

        about = self.menu_help.addAction("&About")
        about.triggered.connect(self.show_about)

        # Status bar. ##################################################
        sb = self.statusBar()
        l = QtWidgets.QLabel("Welcome to pscic v0.0") # TODO: do something useful here
        sb.addPermanentWidget(l)

        # Other settings and decorations. ##############################
        self.setWindowTitle("pscic")

        # Prepare sub-windows. #########################################
        self.__hw = None
        self.__aw = None

        # Init mode display. ###########################################
        self.update_mode_field()

    def calculate(self):
        expr = self.input_field.text()

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
            if self.exact_or_float.isChecked():
                val = tree.evaluate_simplify()
            else:
                val = tree.evaluate()
        except ValueError as e:
            self.output_field.setText(
                r'<span style="color:red;">ValueError: {!s}</span>'.format(e)
            )
            return
        # Output.
        if isinstance(val, Q_):
            # pretty-print units.
            val = "= {:H~}".format(val)
        elif isinstance(val, operators.Equality.Solutions):
            val = "<br>".join(
                "<i>{!s}</i> = {}".format(
                    val.x,
                    ("{:H~}".format(sol)
                     if isinstance(sol, Q_)
                     else "{!s}".format(sol))
                )
                for sol in val.solutions)
        elif isinstance(val, bool):
            val = str(val)
        else:
            val = "= {!s}".format(val)
        self.output_field.setText(r'<span style="font-size: x-large;">'
                                  + val
                                  + r'</span>')

    def update_mode_field(self):
        self.mode_field.setText(
            r'<span style="font-size: small;">'
            + "{}{}"
            "".format(
                ("EXACT " if self.exact_or_float.isChecked() else ""),
                "RAD",
            )
            + r'</span>'
        )

    def show_help(self):
        if not self.__hw:
            self.__hw = HelpWindow()
        self.__hw.show()

    def show_about(self):
        if not self.__aw:
            self.__aw = AboutWindow()
        self.__aw.show()


def main(argv):
    app = QtWidgets.QApplication(argv)

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "logo-path.svg")
    icon = QtGui.QIcon(icon_path)
    app.setWindowIcon(icon)

    main_window = MainWindow()
    main_window.show()

    return app.exec_()
