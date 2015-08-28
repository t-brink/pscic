#!/usr/bin/env python3

from psciclib import parseexpr

while True:
    try:
        expr = input("> ")
    except EOFError:
        print()
        break
    tree = parseexpr.parse(expr)
    print(tree)
    val = tree.evaluate()
    print("=", val)
