"""Built-in Settings update strategies.

This module contains the basic and default update strategies used
when calling `concrete_settings.Settings.update`
"""
import abc

from typing_extensions import Protocol


class Strategy(Protocol):
    @abc.abstractmethod
    def __call__(self, current_value, new_value):
        ...


def overwrite(current_val, new_value):
    return new_value


def append(current_val, new_value):
    return current_val + new_value


def prepend(current_value, new_value):
    return new_value + current_value


default: Strategy = overwrite
