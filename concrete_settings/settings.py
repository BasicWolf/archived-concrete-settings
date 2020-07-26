import logging
import types
from collections import defaultdict
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Mapping,
    Tuple,
    Type,
    Union,
)

from .setting import Setting, PropertySetting
from .setting_registry import registry
from .docreader import extract_doc_comments_from_class_or_module
from .exceptions import StructureError, ValidationError, ValidationErrorDetails
from .sources import get_source, AnySource, Source, NotFound
from .sources.strategies import Strategy, default as default_update_strategy
from .types import GuessSettingType, type_hints_equal
from .validators import Validator, ValueTypeValidator

logger = logging.getLogger(__name__)

INVALID_SETTINGS = '__invalid__settings__'


class SettingsMeta(type):
    def __new__(mcs, name, bases, class_dict):
        new_dict = mcs.class_dict_to_settings(class_dict, bases)
        mcs.add_settings_help(name, new_dict)
        return super().__new__(mcs, name, bases, new_dict)

    @classmethod
    def class_dict_to_settings(mcs, class_dict: dict, bases: List[type]):
        new_dict = {}
        annotations = class_dict.get("__annotations__", {})

        for name, attr in class_dict.items():
            attr_is_setting = isinstance(attr, Setting)
            new_attr = attr

            # Make a Setting out of each UPPERCASE_ATTRIBUTE
            if (
                not attr_is_setting
                and mcs._is_setting_name(name)
                and mcs._can_be_converted_to_setting_automatically(attr)
            ):
                new_attr = mcs._make_setting_from_attribute(name, attr, annotations)

            new_attr_is_setting = isinstance(new_attr, Setting)

            # Should we guess a type_hint for the Setting?
            if new_attr_is_setting and new_attr.type_hint is GuessSettingType:
                new_attr.type_hint = mcs._guess_type_hint(
                    name, new_attr, annotations, bases
                )

            # If the Setting was created from an implicit definition (without behaviors!)
            # should we then try substituting the setting type with a one
            # from the registry?
            if not attr_is_setting and new_attr_is_setting:
                setting_class_from_registry = registry.get_setting_class_for_type(
                    new_attr.type_hint
                )
                if setting_class_from_registry is not Setting:
                    new_attr = mcs._substitute_by_setting_class_from_registry(
                        new_attr,
                        setting_class_from_registry
                    )

            # Final touch: apply behaviors
            if new_attr_is_setting:
                mcs._apply_behaviors(new_attr)

            new_dict[name] = new_attr

        return new_dict

    @classmethod
    def _make_setting_from_attribute(
        mcs, name, attr, annotations
    ) -> Union[PropertySetting, Setting]:
        # is it a class method?
        if isinstance(attr, types.FunctionType):
            return PropertySetting(attr)

        type_hint = annotations.get(name, GuessSettingType)

        setting_class_from_registry = registry.get_setting_class_for_type(type_hint)

        return setting_class_from_registry(attr, doc="", type_hint=type_hint)

    @classmethod
    def _guess_type_hint(mcs, name, setting: Setting, annotations, bases: List[type]):
        # we still have to check annotations,
        # e.g. if the setting was instantiated by behavior
        annotation_type_hint = annotations.get(name, GuessSettingType)
        if annotation_type_hint is not GuessSettingType:
            return annotation_type_hint

        # try to get the type hint from the base classes
        for base in bases:
            try:
                base_type_hint = getattr(base, name).type_hint
                return base_type_hint
            except AttributeError:
                pass

        guessed_setting_type = GuessSettingType.guess_type_hint(setting.value)
        return guessed_setting_type

    @classmethod
    def _is_setting_name(mcs, name: str) -> bool:
        """Return True if name is written in the upper case"""
        return not name.startswith('_') and name.upper() == name

    @classmethod
    def _can_be_converted_to_setting_automatically(mcs, attr: Any) -> bool:
        """Return False if attribute should not be converted
           to a Setting automatically"""
        callable_types = (property, classmethod, staticmethod)
        return not isinstance(attr, callable_types)

    @classmethod
    def add_settings_help(mcs, cls_name: str, class_dict: dict):
        if '__module__' not in class_dict:
            # class is not coming from a module
            return

        settings = {
            name: attr for name, attr in class_dict.items() if isinstance(attr, Setting)
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

        comments = extract_doc_comments_from_class_or_module(cls_module_name, cls_name)

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

    @classmethod
    def _substitute_by_setting_class_from_registry(
        mcs,
        setting: Setting,
        substitue_setting_type: Type[Setting]
    ):
        new_setting = substitue_setting_type(
            setting.value,
            doc=setting.__doc__,
            validators=setting.validators,
            type_hint=setting.type_hint,
            override=setting.override
        )

        new_setting.behaviors = setting.behaviors
        return new_setting

    @classmethod
    def _apply_behaviors(mcs, setting: Setting):
        for behavior in setting.behaviors:
            behavior.decorate(setting)


class Settings(Setting, metaclass=SettingsMeta):
    default_validators: Tuple[Validator, ...] = ()
    mandatory_validators: Tuple[Validator, ...] = (ValueTypeValidator(),)

    _is_being_validated: bool

    _errors: ValidationErrorDetails = {}

    def __init__(self, **kwargs):
        assert (
            'value' not in kwargs
        ), '"value" argument should not be passed to Settings.__init__()'
        assert (
            'type_hint' not in kwargs
        ), '"type_hint" argument should not be passed to Settings.__init__()'

        super().__init__(value=self, type_hint=self.__class__, **kwargs)

        self._is_being_validated = False
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
        # 2. Store found settings as {name: [cls, ...]} to settings_classes
        settings_classes: Dict[str, List[Type['Settings']]] = defaultdict(list)

        assert self.__class__.__mro__[-3] is Settings

        # __mro__[:-2] - skip Settings and object bases
        for cls in reversed(self.__class__.__mro__[:-3]):
            for attr, val in cls.__dict__.items():
                if isinstance(val, Setting):
                    settings_classes[attr].append(cls)
        return dict(settings_classes)

    def _settings_diff(self, s0: Setting, s1: Setting) -> List[str]:
        NO_DIFF = []  # type: ignore
        differences = []

        # No checks are performed if setting is overridden
        if s1.override:
            return NO_DIFF

        if not type_hints_equal(s0.type_hint, s1.type_hint):
            differences.append(f'types differ: {s0.type_hint} != {s1.type_hint}')

        return differences

    @classmethod
    def settings_attributes(cls) -> Iterator[Tuple[str, Setting]]:
        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, Setting):
                yield name, attr

    def is_valid(self, raise_exception=False) -> bool:
        self._errors = {}
        self._errors = self._run_validation(raise_exception)
        return self._errors == {}

    def _run_validation(self, raise_exception=False) -> ValidationErrorDetails:
        self._is_being_validated = True
        errors = {}

        # validate each setting individually
        for name, setting in self.settings_attributes():
            setting_errors = self._validate_setting(name, setting, raise_exception)
            if setting_errors:
                errors[name] = setting_errors

        if errors == {}:
            try:
                self.validate()
            except ValidationError as e:
                if raise_exception:
                    raise e
                else:
                    errors[INVALID_SETTINGS] = [str(e)]

        self._is_being_validated = False
        return errors

    def _validate_setting(
        self, name: str, setting: Setting, raise_exception=False
    ) -> ValidationErrorDetails:
        value: Setting = getattr(self, name)

        errors: List[ValidationErrorDetails] = []
        validators = setting.validators or self.default_validators
        validators += self.mandatory_validators

        for validator in validators:
            try:
                validator(value, name=name, owner=self, setting=setting)
            except ValidationError as e:
                if raise_exception:
                    raise ValidationError({name: e.details}) from e
                errors.append(str(e))
            except Exception as e:
                if raise_exception:
                    raise ValidationError({name: str(e)}) from e
                else:
                    errors.append(str(e))

        # nested Settings
        if isinstance(value, Settings):
            nested_settings = value
            try:
                nested_settings.is_valid(raise_exception=raise_exception)
            except ValidationError as e:
                assert raise_exception
                e.prepend_source(name)
                raise ValidationError({name: e.details}) from e

            if nested_settings.errors:
                errors.append(nested_settings.errors)

        return errors

    def validate(self):
        pass

    def update(self, source: AnySource, strategies: dict = None):
        strategies = strategies if strategies is not None else {}
        assert isinstance(strategies, Mapping), '`strategies` type should be `dict`'

        source_obj = get_source(source)
        self._update(self, source_obj, parents=(), strategies=strategies)

    @staticmethod
    def _update(
        settings: 'Settings',
        source: Source,
        parents: Tuple[str, ...] = (),
        strategies: Dict[str, Strategy] = None,
    ):
        """Recursively update settings object from dictionary"""
        strategies = strategies or {}

        for name, setting in settings.settings_attributes():
            if isinstance(setting, Settings):
                settings._update(setting, source, (*parents, name), strategies)
            else:
                full_setting_name = f'{".".join(parents) and "."}{name}'

                if full_setting_name in strategies:
                    update_strategy = strategies[full_setting_name]
                    logger.debug(
                        'Updating setting %s with strategy %s',
                        full_setting_name,
                        getattr(update_strategy, '__qualname__', 'unknown strategy'),
                    )
                else:
                    update_strategy = default_update_strategy

                update_to_val = source.read(setting, parents)
                if update_to_val is NotFound:
                    continue

                current_val = getattr(settings, name)
                new_val = update_strategy(current_val, update_to_val)
                setattr(settings, name, new_val)

    def extract_to(self, destination: Union[types.ModuleType, dict], prefix: str = ''):
        if prefix != '':
            prefix = prefix + '_'

        if isinstance(destination, types.ModuleType):
            destination = destination.__dict__

        for name, attr in self.settings_attributes():
            var_name = prefix + name
            if isinstance(attr, Settings):  # nested settings
                attr.extract_to(destination, var_name)
            else:
                destination[var_name] = getattr(self, name)

    @property
    def errors(self) -> ValidationErrorDetails:
        return self._errors

    @property
    def is_being_validated(self) -> bool:
        return self._is_being_validated
