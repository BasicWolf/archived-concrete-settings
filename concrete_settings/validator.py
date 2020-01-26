import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .concrete_settings import Setting, Settings


class Validator(metaclass=abc.ABCMeta):
    """A validator is a callable that raises an exception if a value is wrong.

    A validator accepts a value as a mandatory argument, and keyword-only arguments
    referring to settings, setting and setting's name."""

    @abc.abstractmethod
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
