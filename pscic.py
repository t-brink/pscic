#!/usr/bin/env python3

from psciclib import parseexpr, evaluate

while True:
    try:
        expr = input("> ")
    except EOFError:
        print()
        break
    tree = parseexpr.parse(expr)
    print(tree)
    val = evaluate.evaluate(tree)
    print("=", val)
