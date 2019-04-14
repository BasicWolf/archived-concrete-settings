import types
import warnings
from collections import defaultdict
from typing import Any, Callable, Sequence, Union, Dict, List, DefaultDict

from . import docreader
from .exceptions import SettingsStructureError, SettingsValidationError
from .validators import DeprecatedValidator, ValueTypeValidator, Validator
from .utils import guess_type_hint


class Undefined:
    """A special value for which indicates
    that something has not been explicitly set by a user.
    """

    pass


class GuessSettingType:
    """A special value for Setting.type_hint, which indicates
       that a Setting type should be guessed from the default value."""

    pass


# ==== Settings classes ==== #
# ========================== #


class Setting:
    __slots__ = ('value', 'type_hint', 'validators', 'name', '__doc__')

    value: Any
    type_hint: Any
    validators: List[Callable]

    def __init__(
        self,
        value: Any = Undefined,
        doc: Union[str, Undefined] = Undefined,
        validators: Union[Sequence[Callable]] = (),
        type_hint: Any = GuessSettingType,
    ):
        self.value = value
        self.type_hint = type_hint
        self.validators = tuple(validators)

        self.__doc__ = doc

        self.name = ""

    def __set_name__(self, _, name):
        self.name = name

    def __get__(self, settings: 'Settings', settings_type):
        # == class-level access ==
        if not settings:
            return self

        # == object-level access ==
        return getattr(settings, f"__setting_{self.name}_value", self.value)

    def __set__(self, settings: 'Settings', val):
        assert isinstance(
            settings, Settings
        ), "settings should be an instance of Settings"
        setattr(settings, f"__setting_{self.name}_value", val)


class OverrideSetting(Setting):
    pass


class DeprecatedSetting(Setting):
    __slots__ = Setting.__slots__ + ('deprecation_message',)

    def __init__(
        self,
        *args,
        deprecation_message: str = 'Setting `{name}` in class `{cls}` is deprecated.',
        validate_as_error=False,
        **kwargs,
    ):
        """
        :param deprecation_message: The deprecation warning message template.
                                    Formatting arguments:
                                    * name - setting name.
                                    * cls - settings class.
        :param validate_as_error: Fail validation with deprecation message as error.
        """
        super().__init__(*args, **kwargs)

        self.validators = (
            DeprecatedValidator(deprecation_message, validate_as_error),
        ) + self.validators

        self.deprecation_message = deprecation_message

    def __get__(self, settings, settings_type):
        if settings and not settings.validating:
            msg = self.deprecation_message.format(cls=settings_type, name=self.name)
            warnings.warn(msg, DeprecationWarning)
        return super().__get__(settings, settings_type)

    def __set__(self, settings, val):
        if not settings.validating:
            msg = self.deprecation_message.format(cls=type(settings), name=self.name)
            warnings.warn(msg, DeprecationWarning)
        return super().__set__(settings, val)


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
        self._validate_structure()

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

    def _validate_structure(self):
        # validate whether the setting on Nth level of the inheritance hierarchy
        # corresponds to the setting on N-1th level of the hierarchy.
        for name, classes in self._settings_classes.items():
            for c0, c1 in zip(classes, classes[1:]):
                # start with setting object of the first classes
                s0 = c0.__dict__[name]
                s1 = c1.__dict__[name]
                diff = self._settings_diff(s0, s1)
                if diff:
                    raise SettingsStructureError(
                        f'in classes {c0} and {c1} setting {name} has'
                        f' the following difference(s): {diff}'
                    )

    def _settings_diff(self, s0: Setting, s1: Setting) -> Union[None, Dict]:
        # No checks are performed if setting is overriden
        if isinstance(s1, OverrideSetting):
            return None

        if s0.type_hint != s1.type_hint:
            return f'types differ: {s0.type_hint} != {s1.type_hint}'

        return None

    def is_valid(self, raise_exception=False) -> bool:
        """Validate settings and return a boolean indicate whether settings are valid"""
        if not self._validated:
            self._validate(raise_exception)
        return self.errors == {}

    def _validate(self, raise_exception=False):
        self.validating = True
        errors = defaultdict(list)

        # validate each setting individually
        for name in self._settings_classes:
            try:
                self._validate_setting(name)
            except SettingsValidationError as e:
                if raise_exception:
                    raise e
                errors[name].append(str(e))

        self.errors = errors
        self.validating = False
        self._validated = True

    def _validate_setting(self, name: str) -> Sequence[str]:
        setting = getattr(self.__class__, name)
        value = getattr(self, name)

        errors = []
        validators = setting.validators or self.default_validators
        validators += self.mandatory_validators

        for validator in validators:
            if isinstance(validator, Validator):
                validator.set_context(self, setting, name)
            error = validator(value)
            if error:
                errors.append(error)
        return errors
