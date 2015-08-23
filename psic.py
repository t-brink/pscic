#!/usr/bin/env python3

from psiclib import parseexpr, evaluate

while True:
    expr = input("> ")
    tree = parseexpr.parse(expr)
    print(tree)
    val = evaluate.evaluate(tree)
    print("=", val)
