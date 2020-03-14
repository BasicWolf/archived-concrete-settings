import collections
import functools
import logging
import re
import types
from collections import defaultdict
from typing import Any, Callable, Dict, Type, Union, List, Tuple, Iterable, Iterator

from .docreader import extract_doc_comments_from_class_or_module
from .exceptions import StructureError, ValidationError, ValidationErrorDetail
from .sources import get_source, AnySource, Source, NotFound
from .sources.strategies import default as default_update_strategy
from .types import Undefined, GuessSettingType, type_hints_equal, Validator
from .validators import ValueTypeValidator

logger = logging.getLogger(__name__)

INVALID_SETTINGS = '__invalid__settings__'


# ==== Settings classes ==== #
# ========================== #
class Setting:
    value: Any
    type_hint: Any
    validators: Tuple[Validator, ...]
    behaviors: 'Behaviors'

    def __init__(
        self,
        value: Any = Undefined,
        *,
        doc: str = '',
        validators: Tuple[Validator, ...] = (),
        type_hint: Any = GuessSettingType,
        behaviors: Union[Iterable, 'Behaviors'] = (),
    ):
        self.value = value
        self.type_hint = type_hint
        self.validators = tuple(validators)
        self.behaviors = Behaviors(behaviors or ())
        self.__doc__ = doc
        self.name = ""
        self.override = False

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
        get_value = functools.partial(
            getattr, owner, f"__setting_{self.name}_value", self.value
        )
        return self.behaviors.get_setting_value(self, owner, get_value)

    def __set__(self, owner: 'Settings', val):
        assert isinstance(owner, Settings), "owner should be an instance of Settings"

        set_value = functools.partial(setattr, owner, f"__setting_{self.name}_value")
        self.behaviors.set_setting_value(self, owner, val, set_value)


class PropertySetting(Setting):
    def __init__(self, *args, **kwargs):
        decorating_without_arguments = (
            len(args) == 1 and len(kwargs) == 0 and callable(args[0])
        )
        if decorating_without_arguments:
            self._init_decorator_without_arguments(args[0])
        else:
            self._init_decorator_with_arguments(*args, **kwargs)

    def _init_decorator_without_arguments(self, fget: Callable):
        super().__init__()
        self.__call__(fget)

    def _init_decorator_with_arguments(self, *args, **kwargs):
        assert len(args) == 0, (
            'No positional arguments should be passed to '
            f'{self.__class__.__name__}.__init__()'
        )
        assert 'value' not in kwargs, (
            '"value" argument should not be passed to '
            f'{self.__class__.__name__}.__init__()'
        )

        super().__init__(value=Undefined, **kwargs)
        self.fget = None

    def __call__(self, fget: Callable):
        # since functools.update_wrapper overwrite self.__doc__
        # we have to temporarily persist it
        doc_before_wrapping = self.__doc__

        functools.update_wrapper(self, fget)

        # Restore __doc__
        self.__doc__ = self.__doc__ or doc_before_wrapping

        # Extract type_hint from fget annotations if needed
        if self.type_hint is GuessSettingType:
            self.type_hint = fget.__annotations__.get('return', self.type_hint)

        self.fget = fget
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

    def __set__(self, owner: 'Settings', val):
        raise AttributeError("Can't set attribute: property setting cannot be set")


class SettingsMeta(type):
    def __new__(mcs, name, bases, class_dict):
        new_dict = mcs.class_dict_to_settings(class_dict, bases)
        mcs._add_settings_help(name, new_dict)
        return super().__new__(mcs, name, bases, new_dict)

    @classmethod
    def class_dict_to_settings(mcs, class_dict: dict, bases: List[type]):
        new_dict = {}
        annotations = class_dict.get("__annotations__", {})

        for name, attr in class_dict.items():
            new_attr = attr

            # Make a Setting out of ALL_UPPERCASE_ATTRIBUTE
            if (
                not isinstance(attr, Setting)
                and mcs._is_setting_name(name)
                and mcs._can_be_converted_to_setting_automatically(attr)
            ):
                new_attr = mcs._make_setting_from_attribute(name, attr, annotations,)

            # Should we try to guess a type_hint for a Setting?
            if isinstance(new_attr, Setting) and new_attr.type_hint is GuessSettingType:
                new_attr.type_hint = mcs._guess_type_hint(
                    name, new_attr, annotations, bases
                )

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
        return Setting(attr, doc="", type_hint=type_hint)

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
    def _add_settings_help(mcs, cls_name: str, class_dict: dict):
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


class Settings(Setting, metaclass=SettingsMeta):
    default_validators: Tuple[Validator, ...] = (ValueTypeValidator(),)
    mandatory_validators: Tuple[Validator, ...] = ()

    _is_being_validated: bool

    _errors: ValidationErrorDetail = {}

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
        # 2. Store found settigns as {name: [cls, ...]} to settings_classes
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

    def _run_validation(self, raise_exception=False) -> ValidationErrorDetail:
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
    ) -> ValidationErrorDetail:
        value: Setting = getattr(self, name)

        errors: List[ValidationErrorDetail] = []
        validators = setting.validators or self.default_validators
        validators += self.mandatory_validators

        for validator in validators:
            try:
                validator(value, name=name, owner=self, setting=setting)
            except ValidationError as e:
                if raise_exception:
                    raise e
                errors.append(str(e))

        # nested Settings
        if isinstance(value, Settings):
            nested_settings = value
            try:
                nested_settings.is_valid(raise_exception=raise_exception)
            except ValidationError as e:
                assert raise_exception
                e.prepend_source(name)
                raise e

            if nested_settings.errors:
                errors.append(nested_settings.errors)

        return errors

    def validate(self):
        pass

    def update(self, source: AnySource, strategies: dict = None):
        strategies = strategies or {}

        source_obj = get_source(source)
        self._update(self, source_obj, parents=(), strategies=strategies)

    def _update(
        self,
        settings: 'Settings',
        source: Source,
        parents: Tuple[str, ...] = (),
        strategies=None,
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
                        update_strategy.__qualname__,
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
    def errors(self) -> ValidationErrorDetail:
        return self._errors

    @property
    def is_being_validated(self) -> bool:
        return self._is_being_validated


class BehaviorMeta(type):
    def __call__(cls, *args, **kwargs):
        # Act as a decorator
        from concrete_settings import Setting

        _decorating_setting_or_method = (
            len(args) == 1
            and len(kwargs) == 0
            and isinstance(args[0], (Setting, types.FunctionType))
        )

        if _decorating_setting_or_method:
            bhv = super().__call__()
            if isinstance(args[0], types.FunctionType):
                setting = PropertySetting(args[0])
            else:
                setting = args[0]

            bhv = super().__call__()
            return bhv(setting)
        else:
            bhv = super().__call__(*args, **kwargs)
            return bhv

    def __rmatmul__(cls, setting: Any):
        from concrete_settings import Setting

        if not isinstance(setting, Setting):
            setting = Setting(setting)

        bhv = cls()
        return bhv(setting)


class Behavior(metaclass=BehaviorMeta):
    """The base class for Setting attributes behaviors."""

    def __call__(self, setting_or_method: Union[Setting, types.FunctionType]):
        setting: Setting

        if isinstance(setting_or_method, types.FunctionType):
            setting = PropertySetting(setting_or_method)
        else:
            setting = setting_or_method
        # Act as a decorator
        return self.inject(setting)

    def __rmatmul__(self, setting: Any):
        from concrete_settings import Setting

        if not isinstance(setting, Setting):
            setting = Setting(setting)

        return self.inject(setting)

    def inject(self, setting: Setting) -> Setting:
        """Inject self to setting behaviors.

        :setting: Setting to which the behavior is injected.
        :return: Passed setting object.
        """
        setting.behaviors.inject(self)
        return setting

    def get_setting_value(self, setting, owner, get_value):
        """Called when setting.__get__() is invoked."""
        return get_value()

    def set_setting_value(self, setting, owner, val, set_value):
        """Called when setting.__set__() is invoked."""
        set_value(val)


class Behaviors(collections.abc.Container):
    """A container for setting behaviors """

    def __init__(self, iterable=()):
        self._container = list(iterable)

    def __len__(self):
        return len(self._container)

    def __getitem__(self, index):
        return self._container[index]

    def __contains__(self, item):
        return item in self._container

    def inject(self, behavior):
        self._container.insert(0, behavior)

    def get_setting_value(self, setting, owner, get_value):
        """Chain and invoke get_setting_value() of each behavior."""

        def _get_value(i=0):
            if i < len(self):
                return self[i].get_setting_value(
                    setting, owner, functools.partial(_get_value, i + 1)
                )
            else:
                return get_value()

        return _get_value()

    def set_setting_value(self, setting, owner, val, set_value):
        """Chain and invoke set_setting_value() of each behavior."""

        def _set_value(v, i=0):
            if i < len(self):
                self[i].set_setting_value(
                    setting, owner, v, functools.partial(_set_value, i=i + 1)
                )
            else:
                set_value(v)

        return _set_value(val)


class override(Behavior):
    def inject(self, setting: 'Setting'):
        setting.override = True
        return super().inject(setting)


identifier_re = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)


class prefix:
    """A decorator for Settings classes which
       appends the defined prefix to each Setting attribute."""

    def __init__(self, prefix: str):
        if not prefix:
            raise ValueError('prefix cannot be empty')

        if not identifier_re.match(prefix):
            raise ValueError('prefix should be a valid Python identifier')

        self.prefix = f'{prefix}_'

    def __call__(self, settings_cls: Type[Settings]) -> Type[Settings]:
        assert issubclass(
            settings_cls, Settings
        ), 'Intended to decorate Settings sub-classes only'

        for name, attr in settings_cls.settings_attributes():
            new_name = f'{self.prefix}{name}'
            if hasattr(settings_cls, new_name):
                raise ValueError(
                    f'{settings_cls} class already has setting attribute named "{name}"'
                )

            delattr(settings_cls, name)
            setattr(settings_cls, new_name, attr)
            attr.name = new_name
        return settings_cls
