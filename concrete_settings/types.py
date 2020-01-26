from typing import Any


class UndefinedMeta(type):
    def __bool__(self):
        return False

    def __str__(self):
        return 'Undefined value'


class Undefined(metaclass=UndefinedMeta):
    """`Undefined` is a special value which indicates
    that something has not been explicitly set by a user.
    """

    pass


class GuessSettingType:
    """A special value for Setting.type_hint, which indicates
    that a Setting type should be guessed from the default value.

    For an `Undefined` or an unknown type, the guessed type hint is `typing.Any`.
    """

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
    if hint1 == hint2:
        return True

    h1 = getattr(hint1, '__origin__', hint1)
    h2 = getattr(hint2, '__origin__', hint2)
    return h1 == h2
