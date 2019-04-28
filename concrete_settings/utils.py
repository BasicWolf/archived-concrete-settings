import typing


def guess_type_hint(val):
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
    return typing.Any

