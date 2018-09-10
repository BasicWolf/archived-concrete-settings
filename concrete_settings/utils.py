import typing

def validate_type(setting, val):
    pass

def guess_type_hint(val):
    known_types = [
        bool, # bool MUST come before int, as e.g. isinstance(True, int) == True
        int,
        float,
    ]

    for t in known_types:
        if isinstance(val, t):
            return t
    return typing.Any
