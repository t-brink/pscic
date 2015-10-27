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
from .widgets.inputwidget import InputWidget
from .widgets.outputwidget import OutputWidget
from .widgets.outputctrls import OutputCtrls


# TODO:            
# * Put parts of the main window into separate custom widgets to reduce
#   clutter
# ** input widget (linedit + parsed expr + modeline)
# ** output widget (output + explanation + pretty printing methods)
# *** this one should actually pretty-print the output (MathML/LaTeX/...)
# ** output modifying widets (exact, normal/sci/eng/simp, ...)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # The main input area. #########################################
        self.input_area = QtWidgets.QWidget(parent=self)

        # Widgets.
        self.input_widget = InputWidget(self.input_area)
        self.input_widget.returnPressed.connect(self.calculate)

        self.output_widget = OutputWidget(parent=self.input_area)

        # Small toolbar to the right.
        #TODO:
        # - button: to base units (easy, pint has a method)
        # - button: to best units (not easy??)
        # - button: computer readable output, for copy-pasting

        # Output controls.
        self.output_ctrls = OutputCtrls()
        def output_ctrls_changed(*args):
            self.update_mode_field(*args)
            # TODO: do not re-calculate, but change the output only     
            #       this needs support in the lower layers              
            self.calculate(self.input_widget.text)
        self.output_ctrls.changed.connect(output_ctrls_changed)

        # Layout for the widgets.
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.input_widget)
        layout.addWidget(self.output_widget)
        layout.addWidget(self.output_ctrls)

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
        self.calc_exact = None
        self.calc_float_display = None
        self.calc_trigmode = None
        self.update_mode_field(*self.output_ctrls.data)

    def calculate(self, expr):
        if not expr.strip():
            # Empty.
            self.input_widget.set_parsed_field("")
            self.output_widget.update_output(None)
            return
        # Parse.
        try:
            tree = parseexpr.parse(expr)
        except (Error, pyparsing.ParseException) as e:
            self.input_widget.set_parsed_field("")
            self.output_widget.update_output(e)
            return
        self.input_widget.set_parsed_field(tree)
        # Evaluate.
        try:
            if self.calc_exact:
                val = tree.evaluate_simplify()
            else:
                val = tree.evaluate()
        except ValueError as e:
            self.output_widget.update_output(e)
            return
        # Output.
        self.output_widget.update_output(val)

    def update_mode_field(self, exact, float_display):
        self.calc_exact = exact
        self.calc_float_display = float_display
        self.calc_trigmode = "rad"
        self.input_widget.update_mode_field(exact, "rad")

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
