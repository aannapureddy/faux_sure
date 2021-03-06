import sys


class REPLException(Exception):
    """Suppress traceback to maintain flow of Ipython"""

    __suppress_context__ = True


class ModelNotFoundError(REPLException):
    pass


class UniqueFieldRequirementException(REPLException):
    pass


class TypeFieldRequirementException(REPLException):
    pass


class ValidatorFieldRequirementException(REPLException):
    pass


class OneToOneException(REPLException):
    pass


def repl_hook(kind, message, traceback):
    if REPLException in kind.__bases__:
        print("{0}: {1}".format(kind.__name__, message))  # Only print Error Type and Message
    else:
        sys.__excepthook__(kind, message, traceback)  # Print Error Type, Message and Traceback


sys.excepthook = repl_hook
