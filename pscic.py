#!/usr/bin/env python3

from psciclib import parseexpr
from psciclib.exceptions import Error
from psciclib.units import Q_

while True:
    try:
        expr = input("> ")
    except EOFError:
        print()
        break
    try:
        tree = parseexpr.parse(expr)
    except Error as e:
        print(e)
        continue
    print(tree)
    try:
        val = tree.evaluate()
    except ValueError as e:
        print("ValueError:", e)
        continue
    if isinstance(val, Q_):
        # pretty-print units.
        val = "{:P~}".format(val)
    print("=", val)
