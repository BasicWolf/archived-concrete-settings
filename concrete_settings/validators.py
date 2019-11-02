import abc
from typing import TYPE_CHECKING

from typeguard import check_type

from .exceptions import SettingsValidationError
from .types import Undefined

if TYPE_CHECKING:
    from .concrete_settings import Setting, Settings


class Validator(metaclass=abc.ABCMeta):
    """A validator is a callable that raises an exception if a value is wrong.

    A validator accepts a value as a mandatory argument, and keyword-only arguments
    referring to settings, setting and setting's name."""

    @abc.abstбractmethod
    def __call__(
        self,
        value,
        *,
        name: str = None,
        owner: 'Settings' = None,
        setting: 'Setting' = None,
    ):
        """Validate a value. Raise `SettingsValidationError` if value is wrong."""
        pass


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
                f'Expected value of type `{type_hint}` '
                f'got value of type `{type(value)}`'
            ) from e
