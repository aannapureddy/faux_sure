"""
Test curries and sauces
"""
import pytest

from numbers import Number

from faux_sures.recipes.curries import max_length, min_length, exact_length, in_range
from faux_sures.not_db import Field, ValidatorFieldRequirementException


@pytest.mark.parametrize("bound", [0, 1, 10, 50])
@pytest.mark.parametrize("inp", ["", "cat", "stevenson", "This is a long string. Hello World!"])
@pytest.mark.parametrize("_function", ["max_length", "min_length", "exact_length"])
def test_string_curries(bound, inp, _function):
    """Test max, min and exact length"""

    if _function == "min_length":
        result = len(inp) >= bound
        func = min_length
    elif _function == "max_length":
        result = len(inp) <= bound
        func = max_length
    elif _function == "exact_length":
        result = len(inp) == bound
        func = exact_length
    else:
        assert False

    partial = func(bound)
    assert result is partial(inp)
    assert partial.__name__ == f"{_function}_{bound}"

    class Simple:
        string_field = Field(str, func(bound))

    simple = Simple()
    if result is True:
        simple.string_field = inp
        assert simple.string_field == inp
    else:
        with pytest.raises(ValidatorFieldRequirementException, match=f"{_function}_{bound}"):
            simple.string_field = inp
        assert simple.string_field is None


@pytest.mark.parametrize("bounds", [(None, 20), (-30, 0), (12.5, 30), (1 / 3, None)])
@pytest.mark.parametrize("inp", [0, 12, 1 / 3, -50, 15, 3.1415 ** 3])
def test_int_range_curry(bounds, inp):
    """Test in_range function"""

    _min, _max = bounds
    if _min is None:
        result = inp <= _max
    elif _max is None:
        result = inp >= _min
    else:
        result = _min <= inp <= _max

    partial = in_range(*bounds)
    assert result is partial(inp)
    assert partial.__name__ == f"in_range_{_min}_to_{_max}"

    class Simple:
        num_field = Field(Number, in_range(*bounds))

    simple = Simple()
    if result is True:
        simple.num_field = inp
        assert simple.num_field == inp
    else:
        with pytest.raises(ValidatorFieldRequirementException, match=f"in_range_{_min}_to_{_max}"):
            simple.num_field = inp
        assert simple.num_field is None
