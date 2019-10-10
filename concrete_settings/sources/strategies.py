def overwrite(old_val, new_val):
    return new_val


def append(old_val, new_val):
    return old_val + new_val


def prepend(old_val, new_val):
    return new_val + old_val


default = overwrite
