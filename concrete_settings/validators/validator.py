import abc
from typing import TYPE_CHECKING

from typing_extensions import Protocol


if TYPE_CHECKING:
    from concrete_settings.core import Setting, Settings


class Validator(Protocol):
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
        """Validate a value. Raise `ValidationError` if value is wrong."""
        ...
