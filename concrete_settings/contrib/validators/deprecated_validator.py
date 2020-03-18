import warnings

from concrete_settings.exceptions import ValidationError
from concrete_settings.validators import Validator


class DeprecatedValidator(Validator):
    def __init__(self, msg, raise_exception: bool = False):
        self.msg = msg
        self.raise_exception = raise_exception

    def __call__(self, value, *, name, owner, **ignore):
        msg = self.msg.format(name=name, owner=type(owner))

        if self.raise_exception:
            raise ValidationError(msg)
        else:
            warnings.warn(msg, DeprecationWarning)
