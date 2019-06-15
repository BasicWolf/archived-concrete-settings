import abc
import warnings
from typing import Callable

from typeguard import check_type

from .exceptions import SettingsValidationError
from .undefined import Undefined


class Validator(metaclass=abc.ABCMeta):
    """A validator is a callable that raises an exception if a value is wrong.

    A validator accepts a value as a mandatory argument, and keyword-only arguments
    referring to settings, setting and setting's name."""

    @abc.abstractmethod
    def __call__(self, value, *, name=None, owner=None, setting=None):
        """Validate a value. Raise `SettingsValidationError` if value is wrong."""
        pass


class DeprecatedValidator(Validator):
    def __init__(self, msg, raise_exception):
        self.msg = msg
        self.raise_exception = raise_exception

    def __call__(self, value, *, name, owner, **ignore):
        msg = self.msg.format(name=name, owner=type(owner))

        if self.raise_exception:
            raise SettingsValidationError(msg)
        else:
            warnings.warn(msg, DeprecationWarning)


class RequiredValidator(Validator):
    def __init__(self, message):
        self.message = message

    def __call__(self, value, *, name, owner, **ignore):
        if value == Undefined:
            msg = self.message.format(name=name, owner=type(owner))
            raise SettingsValidationError(msg)


class ValueTypeValidator(Validator):
    __slots__ = ('type_hint', 'strict')

    def __init__(self, type_hint=None):
        self.type_hint = type_hint

    def __call__(self, value, *, name, setting, **ignore):
        type_hint = setting.type_hint if self.type_hint is None else self.type_hint

        try:
            check_type(name, value, type_hint)
        except TypeError as e:
            raise SettingsValidationError(
                f'Expected value of type `{type_hint}` got value of type `{type(value)}`'
            ) from e
