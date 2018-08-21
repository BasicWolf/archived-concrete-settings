# IDEAS:
# * Exceptions with 'hint', 'colour_message', 'message' fields
#   * common messages about OverrideSettings
#

import copy
import re
import sys
import types
from typing import Any, Callable, Sequence, Union

PY_VERSION = (sys.version_info.major, sys.version_info.minor)
PY_35 = (3, 5)

if PY_VERSION < PY_35:
    raise ImportError('Python < 3.5 is not supported')

ValidatorsOrNone = Union[Callable, Sequence[Callable], None]


class Undefined:
    pass


class GuessSettingType:
    """A special value for Setting.type_hint, which indicates
       that a Setting type should be derived from the default value."""
    pass


def validate_type(setting, val):
    pass


class Setting:
    # TODO: slots

    val: Any
    _type_hint: Any

    def __init__(self,
                 default_val: Any = Undefined,
                 description: str = '',
                 validators: ValidatorsOrNone = (validate_type, ),
                 type_hint: Any = GuessSettingType):

        self.value = default_val
        self.description = description
        self.type_hint = type_hint

        if isinstance(validators, types.FunctionType):
            self.validators = (validators, )
        else:
            self.validators = validators or ()

        self.name = ''
        self.owner_name = ''

    def __set_name__(self, owner, name):
        self.owner_name = owner.__name__
        self.name = name

    @property
    def full_name(self):
        return self.owner_name + '_' + self.name

    @property
    def type_hint(self):
        return self._type_hint

    @type_hint.setter
    def type_hint(self, val):
        if val == GuessSettingType:
            self._type_hint = guess_type_hint(self.value)
        else:
            self._type_hint = val

    def __get__(self, obj, objtype):
        # TODO: VALIDATOR
        if self.value == Undefined:
            raise ValueError(f'Setting {self.full_name} value has not been set')

        if obj:
            # object.field access
            if callable(self.value):
                return self.value(obj)

        return self.value

    def __set__(self, obj, val):
        for validator in self.validators:
            validator(self, val)
        self.value = val


class SealedSetting(Setting):
    pass


class OverrideSetting(Setting):
    pass



class SettingsMeta(type):
    def __new__(cls, name, bases, class_dict):
        base_dict = {}
        for base in bases:
            if not issubclass(base, Settings):
                raise TypeError('Settings class can inherit from from other Settings classes only')
            # TODO:
            if base is not Settings:
                base_dict = base.__dict__

        new_dict = cls.class_dict_to_settings(class_dict)

        if PY_VERSION == PY_35:
            cls._py35_set_name(cls, new_dict)

        new_dict = cls.merge_into_class_dict(new_dict, base_dict)
        cls = super().__new__(cls, name, bases, new_dict)
        return cls

    @classmethod
    def _py35_set_name(self, cls, class_dict):
        '''__set_name__() implementation for Python 3.5'''
        for name, field in class_dict.items():
            if isinstance(field, Setting):
                field.__set_name__(cls, name)

    @classmethod
    def class_dict_to_settings(cls, class_dict):
        new_dict = {}
        annotations = class_dict.get('__annotations__', {})

        for attr, val in class_dict.items():
            if isinstance(val, Setting):
                new_dict[attr] = val
            elif cls.is_setting_name(attr):
                new_dict[attr] = cls.make_setting_from_attr(attr, val, annotations)
            else:
                new_dict[attr] = val
        return new_dict

    @staticmethod
    def make_setting_from_attr(attr, val, annotations):
        if callable(val):
            type_hint = val.__annotations__.get('return', Any)
        else:
            type_hint = annotations.get(attr, GuessSettingType)

        return Setting(val, type_hint=type_hint)

    @staticmethod
    def is_setting_name(name: str) -> bool:
        '''Return true if name is written in upper case'''
        return name.upper() == name

    @classmethod
    def merge_into_class_dict(cls, class_dict, bases_dict):
        new_dict = {}

        for attr, field in class_dict.items():
            if attr not in bases_dict:
                # no extra processing for attributes which
                # are not among bases attributes
                new_dict[attr] = field
                continue

            base_field = bases_dict[attr]
            if not isinstance(field, Setting) and not isinstance(base_field, Setting):
                new_dict[attr] = field
                continue

            new_dict[attr] = cls._merge_fields(attr, field, base_field)

        return new_dict

    @staticmethod
    def _merge_fields(attr, field, base_field):
        # class field is defined as OverrideSetting
        if isinstance(field, OverrideSetting):
            if isinstance(base_field, Setting):
                # TODO: record in history
                pass
            else:
                # TODO: WARNING record in history
                pass

        # class field is defined as Setting, i.e. no override precedence.
        elif isinstance(field, Setting):
            if isinstance(base_field, SealedSetting):
                raise AttributeError(
                    f'TODO: History; Setting "{attr}" in class "[TODO]"'
                    ' is sealed and cannot be changed in class "[TODO]".'
                    ' Define a setting via OverrideSetting() descriptor to override'
                    ' the sealed setting type and value explicitly.'
                )
            elif isinstance(base_field, Setting):
                if field.type_hint == GuessSettingType:
                    # TODO: record in history
                    field.type_hint = base_field.type_hint
                elif field.type_hint != base_field.type_hint:
                    raise AttributeError(
                        f'TODO: History; Setting "{attr}" in class "[TODO]"'
                        ' has a different type hint that definition in class "[TODO]".'
                        ' Define a setting via OverrideSetting() descriptor to override'
                        ' the existing setting type explicitly.'
                    )

                if field.description and field.description != base_field.description:
                    raise AttributeError(
                        f'TODO: History; Setting "{attr}" in class "[TODO]"'
                        ' has a different description than definition in class "[TODO]".'
                        ' Define a setting via OverrideSetting() descriptor to override'
                        ' the existing setting description explicitly.'
                    )
                else:
                    field.description = base_field.description

                field.validators = base_field.validators
                raise Exception('TODO: WRITE A UNIT TEST')


            else:
                raise AttributeError(
                    f'TODO: History; Setting in class "[TODO]" overrides an'
                    ' existing attribute "{attr}" defined in class "[TODO]".'
                    ' Define a setting via OverrideSetting() descriptor to override'
                    ' the attribute explicitly.'
                )
        return field #, diff # <- TODO History


def guess_type_hint(val):
    # TODO: unit tests for this function
    if isinstance(val, int):
        return int
    elif isinstance(val, float):
        return float


class Settings(metaclass=SettingsMeta):
    pass
