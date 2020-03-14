"""Built-in Settings update strategies.

This module contains the basic and default update strategies used
when calling `concrete_settings.Settings.update`
"""
# from typing_extensions import Protocol


def overwrite(old_val, new_val):
    return new_val


def append(old_val, new_val):
    return old_val + new_val


def prepend(old_val, new_val):
    return new_val + old_val


default = overwrite
