import copy
import functools
import os
import re
import sys
import types
from collections import defaultdict, namedtuple
from typing import Any, Callable, Sequence, Union

from .import exceptions
from .utils import guess_type_hint, validate_type

PY_VERSION = (sys.version_info.major, sys.version_info.minor)
PY_35 = (3, 5)

if PY_VERSION < PY_35:
    raise ImportError('Python < 3.5 is not supported')

VALUES_ATTR = '__settings_values__'


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


class _CallableSettingValue:
    """A special wrapper for method-settings, i.e.
    the methods decorated with @setting and  which
    are processed as setting values producers."""
    def __init__(self, f):
        self.f = f

    def __call__(self, env=None):
        return self.f(env)



ValidatorsTypes = Union[_DefaultValidators, Callable, Sequence[Callable], None]
EnvTypes = Union[str, bool, None]


class EnvValueReader:
    __slots__ = ('key', 'default_val')

    def __init__(self, key: str, default_val):
        self.key = key
        self.default_val = default_val

    def read(self):
        try:
            return self._cached_val
        except AttributeError:
            self._cached_val = os.environ.get(self.key, self.default_val)
            return self._cached_val

    @staticmethod
    def from_env(env: EnvTypes, default_val):
        if isinstance(env, EnvValueReader):
            return env
        elif isinstance(env, str):
            return EnvValueReader(env, default_val)
        elif env == True:
            return EnvValueReader(env, default_val)
        return None


class env:
    __slots__=('_name', '_default', '_ignore_missing')

    def __init__(self,
                 name: str = None,
                 default: Any = Undefined,
                 ignore_missing=False):

        self._name = name
        self._default = default
        self._ignore_missing = ignore_missing

    def get(self, name=None):
        if not name and not self._name:
            return self
        elif not name:
            name = self._name

        try:
            return os.environ[name]
        except KeyError:
            if self._ignore_missing:
                return self._default
            else:
                raise



class Setting:
    __slots__ = ('value', 'type_hint', 'validators',
                 'name', 'history', '__doc__')

    value: Any
    type_hint: Any
    validators: Union[Sequence[Callable], _DefaultValidators]

    def __init__(self,
                 default: Any = Undefined,
                 doc: str = '',
                 validators: ValidatorsTypes = _DefaultValidators,
                 type_hint: Any = _GuessSettingType,
                 env: EnvTypes = None):

        self.value = self._get_default_or_env(default)

        self.type_hint = type_hint
        self.__doc__ = doc

        if isinstance(validators, types.FunctionType):
            self.validators = (validators, )
        else:
            self.validators = validators or ()

        self.name = ''

    def _get_default_or_env(self, default):
        if isinstance(default, env):
            return default.get()
        else:
            return default

    def __set_name__(self, _, name):
        self.name = name

        # if self.value has not been yet fetched from environment
        # perhaps the name was not set? --> try fetching here.
        if isinstance(self.value, env):
            self.value = self.value.get(name)

    def __get__(self, obj, objtype):
        # == class-level access ==
        if not obj:
            return self.value

        # == object-level access ==
        if isinstance(self.value, _CallableSettingValue):
            return self.value(obj)
        else:
            return self.get_setting_of_object(obj)

    def get_setting_of_object(self, obj):
        storage = getattr(obj, VALUES_ATTR, {})
        try:
            val = storage[self.name]
        except KeyError:
            val = self.value
        return val

    def __set__(self, obj, val):
        # TODO
        # for validator in self.validators:
        #     validator(self, val)

        if not obj:
            # == class-level access ==
            self.value = val
        else:
            # == object-level access ==
            storage = self.get_objects_values(obj)
            storage[self.name] = val

    def get_objects_values(self, obj):
        # get or initialize object settings storage
        try:
            storage = getattr(obj, VALUES_ATTR)
        except AttributeError:
            storage = {}
            setattr(obj, VALUES_ATTR, storage)
        return storage


class OverrideSetting(Setting):
    pass


class SealedSetting(OverrideSetting):
    pass


class RequiredSetting(OverrideSetting):
    pass


class SettingsMeta(type):
    def __new__(cls, name, bases, class_dict):
        if VALUES_ATTR in class_dict:
            raise AttributeError('{name}.{VALUES_ATTR} should not be defined explicitly.' )

        bases_dict = {}

        # Iterating through bases in reverse to detect the changes in fields
        for base in reversed(bases):
            if not issubclass(base, Settings):
                raise TypeError('Settings class can inherit from from other Settings classes only')

            if base is not Settings:
                bases_dict = cls.merge_settings_class_dicts(base.__name__, base.__dict__, bases_dict)

        new_dict = cls.class_dict_to_settings(class_dict)

        if PY_VERSION == PY_35:
            cls._py35_set_name(cls, new_dict)

        new_dict = cls.merge_settings_class_dicts(name, new_dict, bases_dict)
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
            if (not isinstance(field, Setting)
                and cls.is_setting_name(attr)
                and cls.is_safe_setting_type(field)):
                new_field = cls.make_setting_from_attr(attr, field, annotations)

            # Should we try to guess a type_hint for a Setting?
            if (isinstance(new_field, Setting)
                and new_field.type_hint is _GuessSettingType
                and new_field.value is not Undefined):
                new_field.type_hint = guess_type_hint(new_field.value)

            new_dict[attr] = new_field
        return new_dict

    @staticmethod
    def make_setting_from_attr(attr, val, annotations, env=None):
        if isinstance(val, _CallableSettingValue):
            type_hint = val.__annotations__.get('return', Any)
            doc = val.__doc__
        else:
            type_hint = annotations.get(attr, _GuessSettingType)
            doc = ''

        return Setting(val, doc, type_hint=type_hint, env=env)

    @staticmethod
    def is_setting_name(name: str) -> bool:
        '''Return true if name is written in upper case'''
        return all((
            name.upper() == name,
            not name.startswith('_'),
        ))

    @staticmethod
    def is_safe_setting_type(field: Any) -> bool:
        '''Return false if field should not be converted to setting automatically'''
        callable_types = (
            property,
            types.FunctionType,
            classmethod,
            staticmethod
        )
        return not isinstance(field, callable_types)

    @classmethod
    def merge_settings_class_dicts(cls, class_name, class_dict, bases_dict):
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

                if (field.__doc__
                    and base_field.__doc__
                    and field.__doc__ != base_field.__doc__):
                    raise exceptions.DocDiffersError(attr)
                else:
                    field.__doc__ = base_field.__doc__

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

    def __call__(cls, *args, **kwargs):
        """__init__() of the Settings object"""
        for attr, field in cls.__dict__.items():
            if isinstance(field, RequiredSetting):
                raise exceptions.RequiredSettingIsUndefined(f'{cls.__name__}.{attr}')

        # invoke __init__() of the object
        return super().__call__(*args, **kwargs)


class Settings(metaclass=SettingsMeta):
    pass


def setting(f, env=None):
    val = functools.wraps(f)(_CallableSettingValue(f))
    return Settings.make_setting_from_attr(f.__name__, val, {}, env)


def settings_from_module(mod: types.ModuleType,
                         *,
                         name_filter: Callable[[str], bool] = SettingsMeta.is_setting_name,
                         class_name: str = None):
    class_name = class_name or 'Module_' + mod.__name__

    mod_fields = {
        attr: value for attr, value in vars(mod).items()
        if name_filter(attr)
    }
    bases =  (Settings, )

    settings_cls = SettingsMeta.__new__(SettingsMeta, class_name, bases, mod_fields)
    return settings_cls


SettingsClassOrObj = Union[SettingsMeta, Settings]


class SettingsHistory:
    history: dict

    def __init__(self, settings: SettingsClassOrObj):
        self.history = {}
        self.history.setdefault(list)

        settings_cls = settings.__class__ if isinstance(settings, Settings) else settings
        for attr, field in settings_cls.__dict__.items():
            if isinstance(field, Setting):
                self.history[attr] = self.calculate_history(settings_cls.__mro__, attr)

    def __getattr__(self, name):
        return self.history[name]

    def __getitem__(self, name):
        return self.__getattr__(name)

    def calculate_history(self, settings_cls_mro, attr):
        # iterate over all settings class base classes;
        # skip Object and Settings, which are the last in MRO
        return [
            cls
            for cls in reversed(settings_cls_mro[:-2])
            if attr in cls.__dict__
        ]
