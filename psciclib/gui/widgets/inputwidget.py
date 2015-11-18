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

#import re

from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QSyntaxHighlighter, QTextCursor, QColor
from PyQt5 import QtWidgets

from .. import tips
from ...result import Mode


class InputEdit(QtWidgets.QPlainTextEdit):
    """Line edit tailored to this app."""

    # Parenthesis matching.
    __open_parens = {"(", "[", "{"}
    __close_parens = {"}", "]", ")"}
    __paren_match = {")": "(",
                     "]": "[",
                     "}": "{"}
    # (fg, bg)
    __good_color = (QColor(  0,   0,   0), QColor( 64, 224, 208))
    __bad_color =  (QColor(255, 255, 255), QColor(160,  32, 240))

    # The string contains the contents of the widget.
    returnPressed = pyqtSignal(str)

    # TODO:
    #   * completion drop-down   

    def __init__(self, parent=None):
        super().__init__(parent)

        # Compat for old Qt: make setPlaceholderText a no-op.
        if not hasattr(self, "setPlaceholderText"):
            self.setPlaceholderText = lambda *args: None

        # Display this when empty.
        #self.setPlaceholderText("Enter expression.")
        self.setPlaceholderText(tips.get_a_tip())             

        self.setTabChangesFocus(True)
        self.setLineWrapMode(super().NoWrap)
        # Height one line. We use a hidden QLineEdit to shamefully
        # steal its size data when we are in single-line mode.
        self._line_edit = QtWidgets.QLineEdit(parent=self)
        self._line_edit.hide()
        self.setMinimumHeight(self._line_edit.minimumHeight())

        # Store default max height.
        self.__deflt_max_height = self.maximumHeight()

        # Convert to single line.
        self.single_line = True
        self._set_single_line()

        # Highlight matching parentheses on cursor change.
        self.cursorPositionChanged.connect(self._match_parentheses)
        self.selectionChanged.connect(self._match_parentheses)
        self.setBackgroundVisible(True)

        # Disable scrolling in single-line mode.
        self.verticalScrollBar().valueChanged.connect(self._has_vscrolled)

    def sizeHint(self):
        if self.single_line:
            return self._line_edit.sizeHint()
        else:
            return super().sizeHint()

    def minimumSizeHint(self):
        if self.single_line:
            return self._line_edit.minimumSizeHint()
        else:
            return super().minimumSizeHint()

    def keyPressEvent(self, event):
        if (
                (
                    self.single_line
                    or (event.modifiers() & Qt.ControlModifier)
                )
                and event.key() in (Qt.Key_Enter, Qt.Key_Return)
            ):
            self.returnPressed.emit(self.toPlainText())
            self.setPlaceholderText(tips.get_a_tip())             
            event.accept()
        else:
            super().keyPressEvent(event)

    def _set_single_line(self):
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMaximumHeight(self._line_edit.maximumHeight())

    def _set_multi_line(self):
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMaximumHeight(self.__deflt_max_height)

    def _has_vscrolled(self, to_value):
        # In single-line mode, we do not allow scrolling.
        print("Bad bad bad!")
        if self.single_line and to_value != 0:
            self.verticalScrollBar().setValue(0)

    def toggle_multi_line(self):
        if self.single_line:
            self._set_multi_line()
            self.single_line = False
        else:
            self._set_single_line()
            self.single_line = True
            # Remove newlines from input.
            # TODO:  does windows+mac work?    
            # TODO: mark the positions until text is changed, so that we
            #       can restore the newlines     
            self.setPlainText(self.toPlainText().replace("\n", " "))
        self.updateGeometry()

    def insertFromMimeData(self, source):
        """Remove newlines from pasted text if necessary."""
        if self.single_line:
            # Remove newlines.
            text = source.text()
            mime = QMimeData()
            # TODO:  does windows+mac work?    
            mime.setText(text.replace("\n", " "))
        else:
            mime = source
        super().insertFromMimeData(mime)

    def _match_parentheses(self):
        self.setExtraSelections([]) # clear selections
        cursor = self.textCursor()
        # If the cursor is at the start, matching parentheses makes no
        # sense. If we have selected text, we do not want to highlight
        # parentheses.
        if not cursor.atStart() and not cursor.hasSelection():
            text = self.toPlainText()
            pos = cursor.position()
            char = text[pos-1]
            if char not in self.__close_parens: # TODO: other direction
                return
            # Now we go hunting for the matching paren.
            n = 1
            for pos2 in range(pos-2, -1, -1):
                char2 = text[pos2]
                if char2 in self.__close_parens:
                    n += 1
                elif char2 in self.__open_parens:
                    n -= 1
                    if n == 0:
                        start_paren = pos2
                        break
            end_paren = pos - 1
            if n > 0:
                # mismatched
                start_paren = None
                matched = False
            else:
                # found one.
                matched = (char2 == self.__paren_match[char])
            # Now highlight.
            fg_color, bg_color = \
                self.__good_color if matched else self.__bad_color
            selections = []
            if start_paren is not None:
                start_sel = QtWidgets.QTextEdit.ExtraSelection()
                start_sel.cursor = self.textCursor()
                start_sel.cursor.clearSelection()
                start_sel.cursor.setPosition(start_paren)
                start_sel.cursor.movePosition(QTextCursor.NextCharacter,
                                              QTextCursor.KeepAnchor)
                start_sel.format.setForeground(fg_color)
                start_sel.format.setBackground(bg_color)
                selections.append(start_sel)
            end_sel = QtWidgets.QTextEdit.ExtraSelection()
            end_sel.cursor = self.textCursor()
            end_sel.cursor.clearSelection()
            end_sel.cursor.setPosition(end_paren)
            end_sel.cursor.movePosition(QTextCursor.NextCharacter,
                                        QTextCursor.KeepAnchor)
            end_sel.format.setForeground(fg_color)
            end_sel.format.setBackground(bg_color)
            selections.append(end_sel)
            self.setExtraSelections(selections)


class ElidingLabel(QtWidgets.QLabel):
    """A QLabel which elides text with an ellipsis if it is too long."""

    def __init__(self, text="", prefix="", suffix="",
                 elide=Qt.ElideRight, parent=None):
        super().__init__(text, parent)
        self._full_text = text
        self._prefix = prefix # those can be used for "<span></span>"
        self._suffix = suffix # because they are not elided!
        self._elide = elide
        self._font_metrics = QFontMetrics(self.font())
        self.setText(text)

    def setText(self, text):
        self._full_text = text
        s = self._font_metrics.elidedText(text, self._elide, self.width())
        if s != text:
            # Show tooltip.
            # TODO: linebreaks!!!!!!!  
            self.setToolTip(text)
        else:
            self.setToolTip("")
        super().setText(self._prefix + s + self._suffix)

    def text(self):
        return self._full_text

    def resizeEvent(self, event):
        # Re-calculate elision.
        self.setText(self._full_text)


class InputWidget(QtWidgets.QWidget):

    returnPressed = pyqtSignal(str)
    toggledMultiLine = pyqtSignal(bool) # bool tells if we are multiline

    def __init__(self, parent=None):
        super().__init__(parent)

        # Input line edit
        self.input_field = InputEdit(parent=self)
        self.input_field.returnPressed.connect(self.returnPressed)

        # Parsed expression is displayed here.
        self.parsed_field = ElidingLabel(prefix='<span style="color:gray;">',
                                         suffix='</span>',
                                         elide=Qt.ElideLeft,
                                         parent=self)
        self.parsed_field.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        # Modes are shown here.
        self.mode_field = QtWidgets.QLabel(parent=self)

        # Layout.
        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.input_field, 0, 0, 1, 2) # span 2 cols
        self.input_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Fixed)

        layout.addWidget(self.parsed_field, 1, 0)
        self.parsed_field.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                        QtWidgets.QSizePolicy.Fixed)

        layout.addWidget(self.mode_field, 1, 1)
        self.mode_field.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Fixed)

        self.setLayout(layout)

    @property
    def text(self):
        return self.input_field.toPlainText()

    def update_mode_field(self, exact, trig_mode):
        self.mode_field.setText(
            r'<span style="font-size: small;">'
            + "{}{}{}{}"
            "".format(
                ("PRE " if False else ""),     
                {"best": "BEST ", "base": "BASE ", "deflt": ""}["deflt"],   
                ("EXACT " if exact == Mode.try_exact else ""),
                {"rad": "RAD", "deg": "DEG", "grad": "GRA"}[trig_mode],
            )
            + r'</span>'
        )

    def set_parsed_field(self, parsed_expr):
        self.parsed_field.setText(str(parsed_expr))

    @property
    def is_multi_line(self):
        return not self.input_field.single_line

    def toggle_multi_line(self):
        self.input_field.toggle_multi_line()
        if self.is_multi_line:
            # TODO: make this a temporary overwrite, similar to the
            # QStatusBar feature!      
            self.set_parsed_field("Press Ctrl+Enter to calculate.")
        else:
            # TODO: restore previous contents!!!!!   
            self.set_parsed_field("")
        self.toggledMultiLine.emit(self.is_multi_line)
