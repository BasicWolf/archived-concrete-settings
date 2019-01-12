from typing import Any, Callable, Sequence, Union

from .utils import guess_type_hint, validate_type

# remember __mro__


class Undefined:
    pass


class _GuessSettingType:
    """A special value for Setting.type_hint, which indicates
       that a Setting type should be derived from the default value."""

    pass


class _UndefinedValidators:
    """A special value for Settings.validators, which indicates
    that validators have not beet explicitly set by a user,
    and the Meta.default_validators logic should apply.
    """

    DEFAULT_VALIDATORS = (validate_type,)


ValidatorsTypes = Union[_UndefinedValidators, Sequence[Callable], None]


class Setting:
    __slots__ = ('value', 'type_hint', 'validators', 'name', '__doc__')

    value: Any
    type_hint: Any
    validators: Union[Sequence[Callable], _UndefinedValidators]

    def __init__(
        self,
        default: Any = Undefined,
        doc: str = "",
        validators: ValidatorsTypes = _UndefinedValidators,
        type_hint: Any = _GuessSettingType,
    ):

        self.value = default

        self.type_hint = type_hint
        self.__doc__ = doc

        if isinstance(validators, types.FunctionType):
            self.validators = (validators,)
        else:
            self.validators = validators or ()

        self.name = ''

    def __set_name__(self, _, name):
        self.name = name

    def __get__(self, obj, objtype):
        # == class-level access ==
        if not obj:
            return self.value

        # == object-level access ==
        return getattr(obj, f'__setting_{self.name}_value', self.value)

    def __set__(self, obj, val):
        if not obj:
            # == class-level access ==
            self.value = val
        else:
            # == object-level access ==
            setattr(obj, f'__setting_{self.name}_value', val)


class ConcreteSettingsMeta(type):
    def __new__(cls, name, bases, class_dict):
        new_class_dict = cls.class_dict_to_settings(class_dict)

        if PY_VERSION == PY_35:
            cls._py35_set_name(cls, new_class_dict)

        return super().__new__(cls, name, bases, new_class_dict)

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
            if (
                not isinstance(field, Setting)
                and cls.is_setting_name(attr)
                and cls.is_safe_setting_type(field)
            ):
                new_field = cls.make_setting_from_attr(attr, field, annotations)

            # Should we try to guess a type_hint for a Setting?
            if (
                isinstance(new_field, Setting)
                and new_field.type_hint is _GuessSettingType
                and new_field.value is not Undefined
            ):
                new_field.type_hint = guess_type_hint(new_field.value)

            new_dict[attr] = new_field
        return new_dict

    @staticmethod
    def make_setting_from_attr(attr, val, annotations):
        type_hint = annotations.get(attr, _GuessSettingType)
        doc = "No documentation provided"
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


class ConcreteSettings(metaclass=ConcreteSettingsMeta):
    pass
