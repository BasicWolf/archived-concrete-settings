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

    @staticmethod
    def guess_type_hint(val):
        if val is Undefined:
            return Any

        known_types = [
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

        for t in known_types:
            if isinstance(val, t):
                return t
        return Any
