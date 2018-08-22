def validate_type(setting, val):
    pass

def guess_type_hint(val):
    # TODO: unit tests for this function
    if isinstance(val, int):
        return int
    elif isinstance(val, float):
        return float
