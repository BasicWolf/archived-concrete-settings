import sys
from typing import Any


class UndefinedMeta(type):
    def __bool__(self):
        return False

    def __str__(self):
        return 'Undefined value'


class Undefined(metaclass=UndefinedMeta):
    def __new__(cls, *args, **kwargs):
        raise RuntimeError(f'{cls} should not be instantiated')


class GuessSettingType:
    #: Recognized Setting value types
    KNOWN_TYPES = [
        bool,  # bool MUST come before int, as e.g. isinstance(True, int) == True
        int,
        float,
        complex,
        list,
        tuple,
        range,
        bytes,
        str,
        frozenset,
        set,
        dict,
    ]

    @classmethod
    def guess_type_hint(cls, val):
        if val is Undefined:
            return Any

        for t in cls.KNOWN_TYPES:
            if isinstance(val, t):
                return t
        return Any


def type_hints_equal(hint1, hint2):
    """Returns true if type hints equal.

    For example:

        type_hints_equal(typing.List, list) => True
    """
    assert hint1 is not None
    assert hint2 is not None

    if hint1 is hint2:
        return True

    h1 = getattr(hint1, '__origin__', hint1) or hint1  # `... or hint 1`
    h2 = getattr(hint2, '__origin__', hint2) or hint2  # - protect from `None` value

    if h1 is h2:
        return True

    PYTHON_36 = (3, 6)
    if (sys.version_info.major, sys.version_info.minor) == PYTHON_36:
        h1 = getattr(hint1, '__extra__', hint1)
        h2 = getattr(hint2, '__extra__', hint2)

    return h1 is h2
