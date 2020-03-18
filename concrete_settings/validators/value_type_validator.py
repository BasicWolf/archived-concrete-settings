from typeguard import check_type

from concrete_settings.exceptions import ValidationError
from concrete_settings.types import Undefined
from .validator import Validator


class ValueTypeValidator(Validator):
    def __init__(self, type_hint=None):
        self.type_hint = type_hint

    def __call__(self, value, *, name, setting, **ignore):
        if value is Undefined:
            return

        type_hint = setting.type_hint if self.type_hint is None else self.type_hint

        try:
            check_type(name, value, type_hint)
        except TypeError as e:
            raise ValidationError(
                f'Expected value of type `{type_hint}` '
                f'got value of type `{type(value)}`'
            ) from e
