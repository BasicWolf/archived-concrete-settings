import functools
import types
from collections import defaultdict
from typing import Any, Callable, Dict, Type, Sequence, Union, List, Tuple

from . import docreader
from .behaviors import Behaviors, override
from .exceptions import StructureError, SettingsValidationError, ValidationErrorDetail
from .validators import ValueTypeValidator
from .sources import get_source, TAnySource, Source
from .types import Undefined, GuessSettingType

INVALID_SETTINGS = '__invalid__settings__'


# ==== Settings classes ==== #
# ========================== #
class Setting:
    value: Any
    type_hint: Any
    validators: List[Callable]
    behaviors: 'Behaviors'

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
        assert isinstance(
            owner, (type(None), Settings)
        ), "owner should be None or an instance of Settings"

        # == class-level access ==
        if not owner:
            return self

        # == object-level access ==
        get_value = functools.partial(self.__descriptor__get__, owner, type(owner))
        return self.behaviors.get_setting_value(self, owner, get_value)

    def __set__(self, owner: 'Settings', val):
        assert isinstance(owner, Settings), "owner should be an instance of Settings"

        set_value = functools.partial(self.__descriptor__set__, owner)
        self.behaviors.set_setting_value(self, owner, val, set_value)

    def __descriptor__get__(self, owner, owner_type):
        return getattr(owner, f"__setting_{self.name}_value", self.value)

    def __descriptor__set__(self, owner, val):
        setattr(owner, f"__setting_{self.name}_value", val)


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
        assert isinstance(
            owner, (type(None), Settings)
        ), "owner should be None or an instance of Settings"

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
    def __new__(mcs, name, bases, class_dict):
        new_dict = mcs.class_dict_to_settings(class_dict)
        mcs.add_settings_help(name, new_dict)
        return super().__new__(mcs, name, bases, new_dict)

    @classmethod
    def class_dict_to_settings(mcs: 'ConcreteSettingsMeta', class_dict: dict):
        new_dict = {}
        annotations = class_dict.get("__annotations__", {})

        for attr, field in class_dict.items():
            new_field = field

            # Make a Setting out of ALL_UPPERCASE_ATTRIBUTE
            if (
                not isinstance(field, Setting)
                and mcs.is_setting_name(attr)
                and mcs.is_safe_setting_type(field)
            ):
                new_field = mcs.make_setting_from_attr(attr, field, annotations)

            # Should we try to guess a type_hint for a Setting?
            if (
                isinstance(new_field, Setting)
                and new_field.type_hint is GuessSettingType
            ):
                new_field.type_hint = GuessSettingType.guess_type_hint(new_field.value)

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


class Settings(Setting, metaclass=ConcreteSettingsMeta):
    default_validators: Tuple = (ValueTypeValidator(),)
    mandatory_validators: Tuple = ()

    validating: bool
    validated: bool

    _errors: ValidationErrorDetail = {}

    def __init__(self, **kwargs):
        assert (
            'value' not in kwargs
        ), 'value argument should not be passed to Settings.__init__()'
        super().__init__(self, **kwargs)

        self.validating = False
        self.validated = False
        self._verify_structure()

    def _verify_structure(self):
        # verify whether the setting on Nth level of the inheritance hierarchy
        # corresponds to the setting on N-1th level of the hierarchy.
        for name, classes in self._get_settings_classes().items():
            for c0, c1 in zip(classes, classes[1:]):
                # start with setting object of the first classes
                s0 = c0.__dict__[name]
                s1 = c1.__dict__[name]
                differences = self._settings_diff(s0, s1)
                if differences:
                    diff = '; '.join(differences)
                    raise StructureError(
                        f'in classes {c0} and {c1} setting {name} has'
                        f' the following difference(s): {diff}'
                    )

    def _get_settings_classes(self) -> Dict[str, List[Type['Settings']]]:
        # _settings_classes is helper list which can be used in
        # settings reading and validation routines.
        # 1. Iterate through __mro__ classes in reverse order - so that
        #    iteration happens from the most-base class to the current one.
        # 2. Store found settigns as {name: [cls, ...]} to settings_classes
        settings_classes = defaultdict(list)

        assert self.__class__.__mro__[-3] is Settings

        # __mro__[:-2] - skip ConcreteSettings and object bases
        for cls in reversed(self.__class__.__mro__[:-3]):
            for attr, val in cls.__dict__.items():
                if isinstance(val, Setting):
                    settings_classes[attr].append(cls)
        return dict(settings_classes)

    def _settings_diff(self, s0: Setting, s1: Setting) -> List[str]:
        NO_DIFF = []
        differences = []

        # No checks are performed if setting is overriden
        if any(isinstance(b, override) for b in s1.behaviors):
            return NO_DIFF

        if s0.type_hint != s1.type_hint:
            differences.append(f'types differ: {s0.type_hint} != {s1.type_hint}')

        return differences

    def is_valid(self, raise_exception=False) -> bool:
        """Validate settings and return a boolean indicate whether settings are valid"""
        if not self.validated:
            self._errors = self._run_validation(raise_exception)
        return self._errors == {}

    def _iter_settings_attributes(self):
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name)
            if isinstance(attr, Setting):
                yield name, attr

    def _run_validation(self, raise_exception=False) -> ValidationErrorDetail:
        self.validating = True
        errors = {}

        # validate each setting individually
        for name, setting in self._iter_settings_attributes():
            setting_errors = self._validate_setting(name, setting, raise_exception)
            if setting_errors:
                errors[name] = setting_errors

        if errors == {}:
            try:
                self.validate()
            except SettingsValidationError as e:
                if raise_exception:
                    raise e
                else:
                    errors[INVALID_SETTINGS] = [str(e)]

        self.validating = False
        self.validated = True
        return errors

    def _validate_setting(
        self, name: str, setting: Setting, raise_exception=False
    ) -> ValidationErrorDetail:
        value: Setting = getattr(self, name)

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

        # nested Settings
        if isinstance(value, Settings):
            nested_settings = value
            try:
                nested_settings.is_valid(raise_exception=raise_exception)
            except SettingsValidationError as e:
                assert raise_exception
                e.prepend_source(name)
                raise e

            if nested_settings.errors:
                errors.append(nested_settings.errors)

        return errors

    def validate(self):
        """Validate settings altogether.

        This is a stub method. It is called after individual
        settings' validation is completed without any errors only.
        Override the method in your child Settings classes.

        SettingsValidationError should be raised in case of validation errors.
        """
        pass

    def update(self, *sources: List[TAnySource]):
        for s in sources:
            source = get_source(s)
            self._update(self, source)

    @staticmethod
    def _update(settings: 'Settings', source: Source, parents: Tuple[str] = ()):
        """Recursively update settings object from dictionary"""

        for name, setting in settings._iter_settings_attributes():
            if isinstance(setting, Settings):
                settings._update(setting, source, (*parents, name))
            else:
                setattr(settings, name, source.read(setting, parents))

    @property
    def errors(self):
        return self._errors
