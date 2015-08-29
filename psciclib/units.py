import pint

# For now just init the default.
ureg = pint.UnitRegistry()
ureg.default_format = "~" # print abbreviations by default.
Q_ = ureg.Quantity
UndefinedUnitError = pint.UndefinedUnitError
