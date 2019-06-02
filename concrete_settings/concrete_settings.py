import functools
import types
import typing
from collections import defaultdict
from typing import Any, Callable, Sequence, Union, List, DefaultDict

from concrete_settings.behaviors import Behaviors
from . import docreader
from .exceptions import SettingsStructureError, SettingsValidationError
from .validators import ValueTypeValidator


class UndefinedMeta(type):
    def __bool__(self):
        return False

    def __str__(self):
        return 'Undefined value'


class Undefined(metaclass=UndefinedMeta):
    """`Undefined` is a special value which indicates
    that something has not been explicitly set by a user.
    """

    pass


class GuessSettingType:
    """A special value for Setting.type_hint, which indicates
       that a Setting type should be guessed from the default value.

    For an `Undefined` or an unknown type, the guessed type hint is `typing.Any`.
    """

    pass


# ==== Settings classes ==== #
# ========================== #
class Setting:
    value: Any
    type_hint: Any
    validators: List[Callable]
    behaviors: Behaviors

    def __init__(
        self,
        value: Any = Undefined,
        *,
        doc: Union[str, Undefined] = Undefined,
        validators: Union[Sequence[Callable]] = (),
        type_hint: Any = GuessSettingType,
        behaviors: List = None,
    ):
        self.value = value
        self.type_hint = type_hint
        self.validators = tuple(validators)
        self.behaviors = Behaviors(behaviors or [])

        self.__doc__ = doc

        self.name = ""

    def __set_name__(self, _, name):
        self.name = name

    def __get__(self, owner: 'Settings', owner_type=None):
        # == class-level access ==
        if not owner:
            return self

        # == object-level access ==
        return self.behaviors.get_setting_value(
            self, owner, functools.partial(self.__descriptor__get__, owner, type(owner))
        )

    def __set__(self, owner: 'Settings', val):
        assert isinstance(owner, Settings), "owner should be an instance of Settings"
        self.behaviors.set_setting_value(
            self, owner, val, functools.partial(self.__descriptor__set__, owner)
        )

    def __descriptor__get__(self, owner, owner_type):
        return getattr(owner, f"__setting_{self.name}_value", self.value)

    def __descriptor__set__(self, owner, val):
        setattr(owner, f"__setting_{self.name}_value", val)


class OverrideSetting(Setting):
    pass


class PropertySetting(Setting):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            super().__init__()
            self.__call__(args[0])
        else:
            super().__init__(*args, **kwargs)
            self.fget = None

    def __call__(self, fget: Callable):
        self.fget = fget

        # Extract __doc__ and return type hint from the decorated function
        if not self.__doc__:
            self.__doc__ = fget.__doc__

        if self.type_hint is GuessSettingType:
            self.type_hint = fget.__annotations__.get('return', self.type_hint)
        return self

    def __get__(self, owner: 'Settings', owner_type=None):
        # == class-level access ==
        if not owner:
            return self

        if self.fget is None:
            raise AttributeError("Unreadable attribute")

        return self.behaviors.get_setting_value(
            self, owner, functools.partial(self.fget, owner)
        )


# ==== ConcreteSettings classes ==== #
# ================================== #


class ConcreteSettingsMeta(type):
    def __new__(mcls, name, bases, class_dict):
        new_dict = mcls.class_dict_to_settings(class_dict)
        mcls.add_settings_help(name, new_dict)
        return super().__new__(mcls, name, bases, new_dict)

    @classmethod
    def class_dict_to_settings(mcls: type, class_dict: dict):
        new_dict = {}
        annotations = class_dict.get("__annotations__", {})

        for attr, field in class_dict.items():
            new_field = field

            # Make a Setting out of ALL_UPPERCASE_ATTRIBUTE
            if (
                not isinstance(field, Setting)
                and mcls.is_setting_name(attr)
                and mcls.is_safe_setting_type(field)
            ):
                new_field = mcls.make_setting_from_attr(attr, field, annotations)

            # Should we try to guess a type_hint for a Setting?
            if (
                isinstance(new_field, Setting)
                and new_field.type_hint is GuessSettingType
            ):
                new_field.type_hint = guess_type_hint(new_field.value)

            new_dict[attr] = new_field

        return new_dict

    @staticmethod
    def make_setting_from_attr(attr, val, annotations):
        type_hint = annotations.get(attr, GuessSettingType)
        doc = ""
        return Setting(val, doc=doc, type_hint=type_hint)

    @staticmethod
    def is_setting_name(name: str) -> bool:
        """Return True if name is written in the upper case"""
        return name.upper() == name and not name.startswith("_")

    @staticmethod
    def is_safe_setting_type(field: Any) -> bool:
        """Return False if field should not be converted to a Setting automatically"""
        callable_types = (property, types.FunctionType, classmethod, staticmethod)
        return not isinstance(field, callable_types)

    @staticmethod
    def add_settings_help(cls_name: str, class_dict: dict):
        if '__module__' not in class_dict:
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


class Settings(metaclass=ConcreteSettingsMeta):
    default_validators: tuple = (ValueTypeValidator(),)
    mandatory_validators: tuple = ()

    validating: bool
    _validated: bool
    _settings_classes: DefaultDict[str, List]

    def __init__(self):
        self.validating = False
        self._validated = False
        self._build_internal_helpers()
        self._verify_structure()

    def _build_internal_helpers(self):
        # self._settings_classes is helper list used in
        # settings reading and validation routines.
        # 1. Iterate through __mro__ classes in reverse order - so that
        #    iteration happens from the most-base class to the current one.
        # 2. Store found settigns as {name: [cls, ...]} to settings_classes
        settings_classes = defaultdict(list)

        assert self.__class__.__mro__[-2] is Settings

        # __mro__[:-2] - skip ConcreteSettings and object bases
        for cls in reversed(self.__class__.__mro__[:-2]):
            for attr, val in cls.__dict__.items():
                if isinstance(val, Setting):
                    settings_classes[attr].append(cls)
        self._settings_classes = settings_classes

    def _verify_structure(self):
        # verify whether the setting on Nth level of the inheritance hierarchy
        # corresponds to the setting on N-1th level of the hierarchy.
        for name, classes in self._settings_classes.items():
            for c0, c1 in zip(classes, classes[1:]):
                # start with setting object of the first classes
                s0 = c0.__dict__[name]
                s1 = c1.__dict__[name]
                differences = self._settings_diff(s0, s1)
                if differences:
                    diff = '; '.join(differences)
                    raise SettingsStructureError(
                        f'in classes {c0} and {c1} setting {name} has'
                        f' the following difference(s): {diff}'
                    )

    def _settings_diff(self, s0: Setting, s1: Setting) -> List[str]:
        NO_DIFF = []
        differences = []

        # No checks are performed if setting is overriden
        if isinstance(s1, OverrideSetting):
            return NO_DIFF

        if s0.type_hint != s1.type_hint:
            differences.append(f'types differ: {s0.type_hint} != {s1.type_hint}')

        return differences

    def is_valid(self, raise_exception=False) -> bool:
        """Validate settings and return a boolean indicate whether settings are valid"""
        if not self._validated:
            self._validate(raise_exception)
        return self.errors == {}

    def _validate(self, raise_exception=False):
        self.validating = True
        errors = defaultdict(list)

        # validate each setting individually
        for cls_name in self._settings_classes:
            setting_errors = self._validate_setting(cls_name, raise_exception)
            if setting_errors:
                errors[cls_name] += setting_errors

        self.errors = errors
        self.validating = False
        self._validated = True

    def _validate_setting(self, name: str, raise_exception=False) -> Sequence[str]:
        setting = getattr(self.__class__, name)
        value = getattr(self, name)

        errors = []
        validators = setting.validators or self.default_validators
        validators += self.mandatory_validators

        for validator in validators:
            try:
                validator(value, name=name, owner=self, setting=setting)
            except SettingsValidationError as e:
                if raise_exception:
                    raise e
                errors.append(str(e))
        return errors


def guess_type_hint(val):
    if val is Undefined:
        return Any

    known_types = [
        bool,  # bool MUST come before int, as e.g. isinstance(True, int) == True
        int,
        float,
        complex,
        list,
        tuple,
        range,
        bytes,
        str,
        frozenset,
        set,
        dict,
    ]

    for t in known_types:
        if isinstance(val, t):
            return t
    return typing.Any
