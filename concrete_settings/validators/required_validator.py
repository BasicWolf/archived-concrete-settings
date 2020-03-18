from concrete_settings.exceptions import ValidationError
from concrete_settings.types import Undefined
from .validator import Validator


class RequiredValidator(Validator):
    def __init__(self, message: str = None):
        if message is None:
            message = (
                'Setting `{name}` is required to have a value. '
                'Current value is `Undefined`'
            )
        self.message = message

    def __call__(self, value, *, name, owner, **ignore):
        if value == Undefined:
            msg = self.message.format(name=name)
            raise ValidationError(msg)
