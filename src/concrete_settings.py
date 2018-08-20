import copy
import re
import sys
from typing import Any, Callable, List, Tuple, get_type_hints

PY_VERSION = (sys.version_info.major, sys.version_info.minor)
PY_35 = (3, 5)

if PY_VERSION < PY_35:
    raise ImportError('Python < 3.5 is not supported')


class Undefined:
    pass


def validate_type(settings, new_val):
    pass


class Setting:
    # TODO: slots

    override: bool
    val: Any


    def __init__(self,
                 default_val: Any = Undefined,
                 description: str = '',
                 type_hint: Any = Any,

                 validator: Callable = validate_type,
                 sealed: bool = False,
                 override: bool = False):
        self.val = default_val
        self.type_hint = type_hint
        self.description = description
        self.validator = validator
        self.sealed = sealed
        self.override = override

        self.name = ''
        self.owner_name = ''

    def __set_name__(self, owner, name):
        self.owner_name = owner.__name__
        self.name = name

    @property
    def full_name(self):
        return self.owner_name + '_' + self.name

    def __get__(self, obj, objtype):
        if self.val == Undefined:
            raise ValueError(f'Setting {self.full_name} value has not been set')

        if obj:
            # object.field access
            if callable(self.val):
                return self.val(obj)

        return self.val

    def __set__(self, obj, val):
        if self.sealed:
            raise AttributeError(f'Cannot set sealed setting {self.full_name} value')

        if self.validator:
            self.validator(self, val)
        self.val = val


class OverrideSetting(Setting):
    def __init__(self, *args, **kwargs):
        kwargs['override'] = True
        super().__init__(self, *args, **kwargs)



class SettingsMeta(type):
    def __new__(cls, name, bases, dct):
        for base in bases:
            if not issubclass(base, Settings):
                raise TypeError('Settings class can inherit from from other Settings classes only')

        new_dct = cls.class_dict_to_settings(dct)
        if PY_VERSION == PY_35:
            cls._py35_set_name(cls, new_dct)


        cls = super().__new__(cls, name, bases, new_dct)
        return cls

    @classmethod
    def _py35_set_name(self, cls, dct):
        '''__set_name__() implementation for Python 3.5'''
        for name, field in dct.items():
            if isinstance(field, Setting):
                field.__set_name__(cls, name)

    @classmethod
    def class_dict_to_settings(cls, dct):
        new_dct = {}
        annotations = dct.get('__annotations__', {})

        for attr, val in dct.items():
            if isinstance(val, Setting):
                new_dct[attr] = val
            elif cls.is_setting_name(attr):
                new_dct[attr] = cls.make_setting_from_attr(attr, val, annotations)
            else:
                new_dct[attr] = val
        return new_dct

    @staticmethod
    def make_setting_from_attr(attr, val, annotations):
        class Guess:
            pass

        if callable(val):
            type_hint = val.__annotations__.get('return', Any)
        else:
            type_hint = annotations.get(attr, Guess)
        return Setting(val, type_hint=type_hint)

    @classmethod
    def merge_bases_settings(cls, bases):
        '''
        Iterate through class bases, lookup `Setting` descriptor-fields
        '''
        setting_fields = {}

        # Python resolves base attributes from right to left, i.e. leftmost has precedence.
        # Thus we should iterate in reverse to detect the changed fields:
        for base in reversed(bases):
            for name, base_field in base.__dict__.items():
                # filter Settings
                if not isinstance(base_field, Setting):
                    continue

                # In case of multiple base classes with same settings
                # - Mixins or multiple inheritance,
                # check if setting has already been defined
                # and update its history if required
                if name in setting_fields:
                    old_field = setting_fields[name]
                    old_field.update(base, base_field)
                else:
                    setting_fields[name] = base_field

        return setting_fields

    def update_setting(cls, old_setting, new_setting):
        if not isinstance(new_setting, OverrideSetting):
            raise AttributeError(
                f'Setting {self.name} defined in {self.owner_name} is overriden. '
                'Use OverrideSetting class to override a setting definition explicitly.'
            )

    @staticmethod
    def is_setting_name(name: str) -> bool:
        '''Return true if name is written in upper case'''
        return name.upper() == name


class Settings(metaclass=SettingsMeta):
    pass
