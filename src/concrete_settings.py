from typing import Any, Callable


class Undefined:
    pass


class Guess:
    pass


def validate_type(settings, new_val):
    pass


class Setting:
    val: Any

    def __init__(self,
                 default_val: Any = Undefined,
                 type_hint: Any = Guess,
                 description: str = '',
                 validator: Callable = validate_type,
                 sealed: bool = False):
        self.val = default_val
        self.type_hint = type_hint
        self.description = description
        self.sealed = sealed
        self.validator = validator

        self.name = ''
        self.owner_name = ''
        self.full_name = ''

    def __set_name__(self, owner, name):
        self.owner_name = owner.__name__
        self.name = name
        self.full_name = self.owner_name + '_' + self.name

    def __get__(self, obj, objtype):
        if self.val == Undefined:
            raise ValueError(f'Setting {self.full_name} value has not been set')

        return self.val

    def __set__(self, obj, val):
        if self.sealed:
            raise AttributeError(f'Cannot set sealed setting {self.full_name} value')

        if self.validator:
            self.validator(self, val)

        self.val = val
