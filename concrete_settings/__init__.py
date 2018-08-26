# IDEAS:
# * Exceptions with 'hint', 'colour_message', 'message' fields
#   * common messages about OverrideSettings
#
import copy
import re
import sys
import types
from typing import Any, Callable, Sequence, Union

from .import exceptions
from .utils import guess_type_hint, validate_type

PY_VERSION = (sys.version_info.major, sys.version_info.minor)
PY_35 = (3, 5)

if PY_VERSION < PY_35:
    raise ImportError('Python < 3.5 is not supported')


class Undefined:
    pass


class _GuessSettingType:
    """A special value for Setting.type_hint, which indicates
       that a Setting type should be derived from the default value."""
    pass


class _DefaultValidators:
    """A special value for Settings.validators, which indicates
    that validators have not beet explicitly set by a user,
    and the default validators logic should apply.
    """
    VALIDATORS = (validate_type, )



ValidatorsOrNone = Union[_DefaultValidators, Callable, Sequence[Callable], None]


class Setting:
    __slots__ = ('value', 'type_hint', 'description', 'validators',
                 'name', 'owner_name')

    value: Any
    type_hint: Any
    description: str
    validators: Union[Sequence[Callable], _DefaultValidators]

    def __init__(self,
                 default_val: Any = Undefined,
                 description: str = '',
                 validators: ValidatorsOrNone = _DefaultValidators,
                 type_hint: Any = _GuessSettingType):

        self.value = default_val
        self.description = description
        self.type_hint = type_hint

        if isinstance(validators, types.FunctionType):
            self.validators = (validators, )
        else:
            self.validators = validators or ()

        self.name = ''
        # TODO: do we actually need this?
        self.owner_name = ''

    def __set_name__(self, owner, name):
        self.owner_name = owner.__name__
        self.name = name

    @property
    def full_name(self):
        return self.owner_name + '_' + self.name

    def __get__(self, obj, objtype):
        # TODO: VALIDATOR
        if self.value == Undefined:
            raise exceptions.UndefinedValueError(f'Setting {self.full_name} value has not been set')

        if obj:
            # object.field access
            if callable(self.value):
                return self.value(obj)

        return self.value

    def __set__(self, obj, val):
        # TODO
        # for validator in self.validators:
        #     validator(self, val)
        self.value = val


class OverrideSetting(Setting):
    pass


class SealedSetting(OverrideSetting):
    pass



class SettingsMeta(type):
    def __new__(cls, name, bases, class_dict):
        bases_dict = {}

        # Iterating through bases in reverse to detect the changes in fields
        for base in reversed(bases):
            if not issubclass(base, Settings):
                raise TypeError('Settings class can inherit from from other Settings classes only')

            if base is not Settings:
                bases_dict = cls.merge_settings_class_dicts(base.__dict__, bases_dict)

        new_dict = cls.class_dict_to_settings(class_dict)

        if PY_VERSION == PY_35:
            cls._py35_set_name(cls, new_dict)

        new_dict = cls.merge_settings_class_dicts(new_dict, bases_dict)
        new_dict = cls.setup_defaults(new_dict)

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

        for attr, field in class_dict.items():
            new_field = field

            # Make a Setting out of ALL_UPPERCASE_ATTRIBUTE
            if not isinstance(field, Setting) and cls.is_setting_name(attr):
                new_field = cls.make_setting_from_attr(attr, field, annotations)

            # Should we try to guess a type_hint for a Setting?
            if (isinstance(new_field, Setting)
                and new_field.type_hint is _GuessSettingType
                and new_field.value is not Undefined):
                new_field.type_hint = guess_type_hint(new_field.value)

            new_dict[attr] = new_field
        return new_dict

    @staticmethod
    def make_setting_from_attr(attr, val, annotations):
        if callable(val):
            type_hint = val.__annotations__.get('return', Any)
        else:
            type_hint = annotations.get(attr, _GuessSettingType)

        return Setting(val, type_hint=type_hint)

    @staticmethod
    def is_setting_name(name: str) -> bool:
        '''Return true if name is written in upper case'''
        return name.upper() == name

    @classmethod
    def merge_settings_class_dicts(cls, class_dict, bases_dict):
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
                raise exceptions.SealedSettingError(attr)

            elif isinstance(base_field, Setting):
                if field.type_hint == _GuessSettingType:
                    # TODO: record in history
                    field.type_hint = base_field.type_hint
                elif field.type_hint != base_field.type_hint:
                    raise exceptions.TypeHintDiffersError(attr)

                if (field.description
                    and base_field.description
                    and field.description != base_field.description):
                    raise exceptions.DescriptionDiffersError(attr)
                else:
                    field.description = base_field.description

                if field.validators is _DefaultValidators:
                    # Apply special logic by copying the base field validators
                    field.validators = base_field.validators
                elif not set(field.validators).issuperset(set(base_field.validators)):
                    raise exceptions.ValidatorsDiffersError(attr)
            else:
                # base_field is NOT a setting, i.e. trying to override a normal class field
                raise exceptions.AttributeShadowError(attr)
        return field #, diff # <- TODO History

    @staticmethod
    def setup_defaults(class_dict):
        """Convert Setting fields defaults stubs to values"""
        for field in class_dict.values():
            if not isinstance(field, Setting):
                continue

            if field.validators is _DefaultValidators:
                field.validators = _DefaultValidators.VALIDATORS

        return class_dict


class Settings(metaclass=SettingsMeta):
    pass


class History:
    pass
