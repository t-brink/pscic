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
import time
import signal

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import pyparsing

from .. import parseexpr
from .. import operators
from .. import version
from .. import result
from ..exceptions import Error
from ..units import Q_
from .helpwindow import HelpWindow
from .aboutwindow import AboutWindow
from .widgets.inputwidget import InputWidget
from .widgets.outputwidget import OutputWidget
from .widgets.outputctrls import OutputCtrls
from .widgets.quickbuttons import QuickButtons
from .widgets.statusbar import StatusBar


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
        self.quick_buttons = QuickButtons(parent=self.input_area)
        self.quick_buttons.input_size_toggled.connect(
            self.input_widget.toggle_multi_line
        )
        self.quick_buttons.base_units_clicked.connect(self.to_base_units)
        self.quick_buttons.best_units_clicked.connect(self.to_best_units)
        self.quick_buttons.copy_paste_clicked.connect(self.copy_paste_mode)
        # Update icon.
        self.quick_buttons.set_input_toggle_btn(self.input_widget.is_multi_line)
        self.input_widget.toggledMultiLine.connect(
            self.quick_buttons.set_input_toggle_btn
        )

        # Output controls.
        self.output_ctrls = OutputCtrls()
        def output_ctrls_changed(*args):
            self.update_mode_field(*args)
            # TODO: do not re-calculate, but change the output only     
            #       this needs support in the lower layers              
            self.calculate(self.input_widget.text)
        self.output_ctrls.changed.connect(output_ctrls_changed)

        # Layout for the widgets.
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.input_widget, 0, 0)
        layout.addWidget(self.quick_buttons, 0, 1, 2, 1)
        layout.addWidget(self.output_widget, 1, 0)
        layout.addWidget(self.output_ctrls, 2, 0, 1, 2)

        # Assign the input area to the main window.
        self.input_area.setLayout(layout)
        self.setCentralWidget(self.input_area)

        # Menu bar. ####################################################
        menu_bar = self.menuBar()

        # File menu.
        self.menu_file = menu_bar.addMenu("&File")

        quit_ = self.menu_file.addAction("&Quit")
        quit_.triggered.connect(QtWidgets.QApplication.quit)

        # Help menu.
        self.menu_help = menu_bar.addMenu("&Help")

        help_ = self.menu_help.addAction("&Help")
        help_.triggered.connect(self.show_help)

        about = self.menu_help.addAction("&About")
        about.triggered.connect(self.show_about)

        # Status bar. ##################################################
        sb = self.statusBar()
        self.sb = StatusBar(sb)

        # Other settings and decorations. ##############################
        self.setWindowTitle(version.progname)

        # Prepare sub-windows. #########################################
        self.__hw = None
        self.__aw = None

        # Init mode display. ###########################################
        self.calc_exact = None
        self.calc_float_display = None
        self.calc_trigmode = None
        self.update_mode_field(*self.output_ctrls.data)

    def _calculate(self, expr, unit_mode):
        if not expr.strip():
            # Empty.
            self.input_widget.set_parsed_field("")
            self.output_widget.update_output(None, None, None, None, None)
            return
        # Parse.
        try:
            tree = parseexpr.parse(expr)
        except (Error, pyparsing.ParseException) as e:
            self.input_widget.set_parsed_field("")
            self.output_widget.update_output(e, None, None, None, None)
            return
        except Exception as e:
            from .widgets.exceptionbox import exception_box
            exception_box(e, self)
            return
        self.input_widget.set_parsed_field(tree)
        # Evaluate.
        try:
            val = tree.evaluate()
        except ValueError as e:
            self.output_widget.update_output(e, None, None, None, None)
            return
        except Exception as e:
            from .widgets.exceptionbox import exception_box
            exception_box(e, self)
            return
        # Output.
        self.output_widget.update_output(
            val, self.calc_exact, self.calc_numeral_system,
            self.calc_precision, unit_mode
        )

    def calculate(self, expr, unit_mode=result.UnitMode.none):
        tic = time.time()
        self._calculate(expr, unit_mode)
        toc = time.time()
        self.sb.set_walltime(toc-tic)

    def update_mode_field(self, exact, float_display, numeral_system,
                          precision):
        self.calc_exact = exact
        self.calc_float_display = float_display
        self.calc_numeral_system = numeral_system
        self.calc_precision = precision
        self.calc_trigmode = "rad"
        self.input_widget.update_mode_field(exact, self.calc_trigmode)

    def to_base_units(self):
        # TODO: do not re-calculate, but re-print the result!
        self.calculate(self.input_widget.text, result.UnitMode.to_base)

    def to_best_units(self):
        # TODO: do not re-calculate, but re-print the result!
        self.calculate(self.input_widget.text, result.UnitMode.to_best)

    def copy_paste_mode(self):
        self.sb.set_tmp("Copy/paste mode not implemented")

    def show_help(self):
        if not self.__hw:
            self.__hw = HelpWindow()
        self.__hw.show()

    def show_about(self):
        if not self.__aw:
            self.__aw = AboutWindow()
        self.__aw.show()


def main(argv, __start): # __start is to time startup, it is a debugging tool!
    app = QtWidgets.QApplication(argv)

    # TODO: use python packaging facilities to get the path      
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "icons", "logo-path.svg")
    icon = QtGui.QIcon(icon_path)
    app.setWindowIcon(icon)

    main_window = MainWindow()
    main_window.show()

    # Install SIGNINT handler.
    signal.signal(signal.SIGINT, lambda *args: QtWidgets.QApplication.quit())

    # Let Python handle signals every 500 ms, so that for example
    # ctrl-c on the command line works.
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: None) # this just drops to python's
                                        # main thread
    timer.start(500)

    import time
    __stop = time.time()
    main_window.sb.set_tmp("Startup took {} s.".format(__stop - __start),
                           timeout=20000)

    return app.exec_()
