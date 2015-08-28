class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class UnknownFunctionError(Error):
    """Function name unknown."""
    def __init__(self, funcname):
        self.funcname = funcname

    def __str__(self):
        return "Unknown function: {!s}".format(self.funcname)

    def __repr__(self):
        return "UnknownFunctionError({!r})".format(self.funcname)


class UnknownConstantError(Error):
    """Unknown constant or variable name."""
    def __init__(self, constname):
        self.constname = constname

    def __str__(self):
        return "Unknown constant or variable: {!s}".format(self.constname)

    def __repr__(self):
        return "UnknownConstantError({!r})".format(self.constname)
