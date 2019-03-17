import os
import sys
import types
from collections import defaultdict
from typing import Any, Callable, Sequence, Union, Dict

from sphinx.pycode.parser import Parser

from . import exceptions, docreader
from .utils import guess_type_hint, validate_type

PY_VERSION = (sys.version_info.major, sys.version_info.minor)
PY_36 = (3, 6)

if PY_VERSION < PY_36:
    raise ImportError("Python 3.6 or higher is required by concrete_settings")


class Undefined:
    """A special value for which indicates
    that something has not been explicitly set by a user.
    """

    pass


class GuessSettingType:
    """A special value for Setting.type_hint, which indicates
       that a Setting type should be derived from the default value."""

    pass


DEFAULT_VALIDATORS = (validate_type,)


# ==== Settings classes ==== #
# ========================== #


class Setting:
    __slots__ = ("value", "type_hint", "validators", "name", "__doc__")

    value: Any
    type_hint: Any
    validators: Union[Sequence[Callable], Undefined]

    def __init__(
        self,
        default: Any = Undefined,
        doc: Union[str, Undefined] = Undefined,
        validators: Union[Sequence[Callable], Undefined] = Undefined,
        type_hint: Any = GuessSettingType,
    ):

        self.value = default

        self.type_hint = type_hint
        self.__doc__ = doc

        if isinstance(validators, types.FunctionType):
            self.validators = (validators,)
        else:
            self.validators = validators or ()

        self.name = ""

    def __set_name__(self, _, name):
        self.name = name

    def __get__(self, obj, objtype):
        # == class-level access ==
        if not obj:
            return self

        # == object-level access ==
        if not obj.is_valid:
            raise exceptions.SettingsNotValidatedError(
                obj.__class__.__name__, self.name
            )

        return getattr(obj, f"__setting_{self.name}_value", self.value)

    def __set__(self, obj, val):
        assert obj is not None, "obj should not be None!"
        setattr(obj, f"__setting_{self.name}_value", val)


class OverrideSetting(Setting):
    pass


class SealedSetting(OverrideSetting):
    pass


# ==== ConcreteSettings classes ==== #
# ================================== #


class ConcreteSettingsMeta(type):
    def __new__(cls, name, bases, class_dict):
        new_dict = cls.class_dict_to_settings(class_dict)
        cls.add_settings_help(name, new_dict)
        return super().__new__(cls, name, bases, new_dict)

    @classmethod
    def class_dict_to_settings(cls: type, class_dict: dict):
        new_dict = {}
        annotations = class_dict.get("__annotations__", {})

        for attr, field in class_dict.items():
            new_field = field

            # Make a Setting out of ALL_UPPERCASE_ATTRIBUTE
            if (
                not isinstance(field, Setting)
                and cls.is_setting_name(attr)
                and cls.is_safe_setting_type(field)
            ):
                new_field = cls.make_setting_from_attr(attr, field, annotations)

            # Should we try to guess a type_hint for a Setting?
            if (
                isinstance(new_field, Setting)
                and new_field.type_hint is GuessSettingType
                and new_field.value is not Undefined
            ):
                new_field.type_hint = guess_type_hint(new_field.value)

            new_dict[attr] = new_field
        return new_dict

    @staticmethod
    def make_setting_from_attr(attr, val, annotations):
        type_hint = annotations.get(attr, GuessSettingType)
        doc = ""
        return Setting(val, doc, type_hint=type_hint)

    @staticmethod
    def is_setting_name(name: str) -> bool:
        """Return true if name is written in upper case"""
        return name.upper() == name and not name.startswith("_")

    @staticmethod
    def is_safe_setting_type(field: Any) -> bool:
        """Return false if field should not be converted to setting automatically"""
        callable_types = (property, types.FunctionType, classmethod, staticmethod)
        return not isinstance(field, callable_types)

    @staticmethod
    def add_settings_help(cls_name: str, class_dict: dict):
        if not '__module__' in class_dict:
            # class is not coming from a module
            return

        settings = {
            attr: field
            for attr, field in class_dict.items()
            if isinstance(field, Setting)
        }
        if not settings:
            # class seems to contain to settings
            return

        if all(setting.__doc__ for setting in settings.values()):
            # All settings of the class have been explicitly documented.
            # Since explicit documentation overrides comment-docs,
            # there is no need to proceed further
            return

        # read the contents of the module which contains the settings
        # and parse it via Sphinx parser
        cls_module_name = class_dict['__module__']

        comments = docreader.extract_doc_comments_from_class_or_module(
            cls_module_name, cls_name
        )

        for name, setting in settings.items():
            if setting.__doc__:
                # do not modify an explicitly-made setting documentation
                continue

            comment_key = (cls_name, name)
            try:
                setting.__doc__ = comments[comment_key]
            except KeyError:
                # no comment-style documentation exists
                pass


class ConcreteSettings(metaclass=ConcreteSettingsMeta):
    def __init__(self):
        self._validated = False
        super().__init__()

    @classmethod
    def from_module(cls, module):
        pass

    def is_valid(self, raise_exception=False) -> bool:
        """Validate settings and return a boolean indicate whether settings are valid"""
        if not self._validated:
            self._validate(raise_exception)
        return self.errors == {}

    def _validate(self, raise_exception=False):
        # 1. Iterate through __mro__ classes in reverse order - so that
        #    iteration happens from the most-base class to the current one.
        # 2. Store found settigns as {name: [cls, ...]} to settings_classes
        # 3. Validate settings_classes
        settings_classes = defaultdict(list)

        assert self.__class__.__mro__[-2] is ConcreteSettings

        # __mro__[:-2] - skip ConcreteSettings and object bases
        for cls in reversed(self.__class__.__mro__[:-2]):
            for attr, val in cls.__dict__.items():
                if isinstance(val, Setting):
                    settings_classes[attr].append(cls)

        errors = defaultdict(list)

        # first, validate each setting individually
        # the goal here is to find out, whether a setting
        # has a valid value on each level of inheritance
        for name, classes in settings_classes.items():
            for cls in classes:
                self.__validate_setting(name, cls)

        # validate whether the setting on Nth level of the class hierarchy
        # corresponds to the setting on N-1th level of the class hierarchy.
        for name, classes in settings_classes.items():
            for c0, c1 in zip(classes, classes[1:]):
                # start with setting object of the first classes
                s0 = c0.__dict__[name]
                s1 = c1.__dict__[name]
                diff = self.__settings_diff(s0, s1)
                if diff:
                    err = (
                        f'in classes {c0} and {c1} setting has'
                        f' the following difference(s): {diff}'
                    )
                    errors[name].append(str(err))

        self.errors = errors
        self._validated = True

        if raise_exception:
            raise exceptions.SettingsValidationError(errors)

    def __validate_setting(self, name: str, cls: 'ConcreteSettings'):
        pass

    def __settings_diff(self, s0, s1) -> Union[None, Dict]:
        # No checks are performed if setting is overriden
        if isinstance(s1, OverrideSetting):
            return None

        # if isinstance(s0, SealedSetting) and s0.value != s1.value:
        #     pass

        if s0.type_hint != s1.type_hint:
            return f'types differ: {s0.type_hint} != {s1.type_hint}'

        return None
