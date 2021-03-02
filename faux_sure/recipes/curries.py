"""
Utilities for simple validators
"""

from numbers import Number
from typing import Callable, Optional


def exact_length(length: int) -> Callable[[str], bool]:
    """
    Create an EXACT length validator

    Args:
        length (int): exact length

    Returns:
        Callable[[str], bool]: a function with the name exact_length_{length}
    """

    def v(_field):
        return len(_field) == length

    v.__name__ = f"exact_length_{length}"
    return v


def min_length(length: int) -> Callable[[str], bool]:
    """
    Create a MIN length validator

    Args:
        length (int): MIN length (inclusive)

    Returns:
        Callable[[str], bool]: a function with the name min_length_{length}
    """

    def v(_field):
        return len(_field) >= length

    v.__name__ = f"min_length_{length}"
    return v


def max_length(length: int) -> Callable[[str], bool]:
    """
    Create an MAX length validator (inclusive)

    Args:
        length (int): MAX length

    Returns:
        Callable[[str], bool]: a function with the name exact_length_{length}
    """

    def v(_field):
        return len(_field) <= length

    v.__name__ = f"max_length_{length}"
    return v


def in_range(_min: Optional[Number] = None, _max: Optional[Number] = None) -> Callable[[Number], bool]:
    """
    Creates a number range validator
    * It can work for any number type

    Args:
        _max (Optional[Number]): max value
        _min (Optional[Number]): min value

    Returns:
        Callable[[Number], bool]: a function with the name in_range_{}_to_{}
    """
    if _min is None and _max is None:
        raise ValueError("Either min or max must be supplied")

    def v(_field):
        return (_min if _min is not None else _field) <= _field <= (_max if _max is not None else _field)

    v.__name__ = f"in_range_{_min}_to_{_max}"
    return v
