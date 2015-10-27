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

from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QSyntaxHighlighter, QTextCursor, QColor
from PyQt5 import QtWidgets


class InputEdit(QtWidgets.QPlainTextEdit):
    """Line edit tailored to this app."""

    # Parenthesis matching.
    __open_parens = {"(", "[", "{"}
    __close_parens = {"}", "]", ")"}
    __paren_match = {")": "(",
                     "]": "[",
                     "}": "{"}
    __good_color = QColor(64, 224, 208)
    __bad_color = QColor(160, 32, 240)

    # The string contains the contents of the widget.
    returnPressed = pyqtSignal(str)

    # TODO:
    #   * completion drop-down   
    #   * can still paste newlines!

    def __init__(self, parent=None):
        super().__init__(parent)

        # Display this when empty.
        #self.setPlaceholderText("Hi there!")

        # Convert to single line.
        self.setLineWrapMode(super().NoWrap)
        self.setTabChangesFocus(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Height one line. We use a hidden QLineEdit to shamefully
        # steal its size data.
        self._line_edit = QtWidgets.QLineEdit(parent=self)
        self._line_edit.hide()
        self.setMinimumHeight(self._line_edit.minimumHeight())
        self.setMaximumHeight(self._line_edit.maximumHeight())

        # Highlight matching parentheses on cursor change.
        self.cursorPositionChanged.connect(self._match_parentheses)
        self.selectionChanged.connect(self._match_parentheses)
        self.setBackgroundVisible(True)

    def sizeHint(self):
        return self._line_edit.sizeHint()

    def minimumSizeHint(self):
        return self._line_edit.minimumSizeHint()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.returnPressed.emit(self.toPlainText())
            event.accept()
        else:
            super().keyPressEvent(event)

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
            bg_color = self.__good_color if matched else self.__bad_color
            selections = []
            if start_paren is not None:
                start_sel = QtWidgets.QTextEdit.ExtraSelection()
                start_sel.cursor = self.textCursor()
                start_sel.cursor.clearSelection()
                start_sel.cursor.setPosition(start_paren)
                start_sel.cursor.movePosition(QTextCursor.NextCharacter,
                                              QTextCursor.KeepAnchor)
                start_sel.format.setBackground(bg_color)
                selections.append(start_sel)
            end_sel = QtWidgets.QTextEdit.ExtraSelection()
            end_sel.cursor = self.textCursor()
            end_sel.cursor.clearSelection()
            end_sel.cursor.setPosition(end_paren)
            end_sel.cursor.movePosition(QTextCursor.NextCharacter,
                                        QTextCursor.KeepAnchor)
            end_sel.format.setBackground(bg_color)
            selections.append(end_sel)
            self.setExtraSelections(selections)


class InputWidget(QtWidgets.QWidget):

    returnPressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Input line edit
        self.input_field = InputEdit(parent=self)
        self.input_field.returnPressed.connect(self.returnPressed)

        # Parsed expression is displayed here.
        self.parsed_field = QtWidgets.QLabel(parent=self)
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
        self.parsed_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
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
            + "{}{}"
            "".format(
                ("EXACT " if exact else ""),
                {"rad": "RAD", "deg": "DEG", "grad": "GRA"}[trig_mode],
            )
            + r'</span>'
        )

    def set_parsed_field(self, parsed_expr):
        self.parsed_field.setText(
            r'<span style="color:gray;">{!s}</span>'.format(parsed_expr)
        )
