import functools
from typing import Any, Tuple, Optional, Union, Callable, TYPE_CHECKING, List

from .types import GuessSettingType, Undefined
from .validators import Validator

if TYPE_CHECKING:
    from .settings import Settings
    from .behaviors import Behavior


class Setting:
    value: Any
    type_hint: Any
    validators: Tuple[Validator, ...]
    name: str
    override: bool
    __doc__: str
    _behaviors: List['Behavior']

    def __init__(
        self,
        value: Any = Undefined,
        *,
        doc: str = '',
        validators: Tuple[Validator, ...] = (),
        type_hint: Any = GuessSettingType,
        override: bool = False,
    ):
        self.value = value
        self.type_hint = type_hint
        self.validators = tuple(validators)
        self.__doc__ = doc
        self.name = ""
        self.override = override

        self._behaviors: List['Behavior'] = []

    def __set_name__(self, _, name):
        self.name = name

    def __get__(
        self, owner: Optional['Settings'], owner_type=None
    ) -> Union[Any, 'Setting']:
        # == class-level access ==
        if not owner:
            return self

        # == object-level access ==
        return self.get_value(owner)

    def get_value(self, owner):
        return getattr(owner, f"__setting_{self.name}_value", self.value)

    def __set__(self, owner: 'Settings', val):
        self.set_value(owner, val)

    def set_value(self, owner: 'Settings', val):
        setattr(owner, f"__setting_{self.name}_value", val)


class PropertySetting(Setting):
    def __init__(self, *args, **kwargs):
        decorating_without_arguments = (
            len(args) == 1 and len(kwargs) == 0 and callable(args[0])
        )
        if decorating_without_arguments:
            self._init_decorator_without_arguments(args[0])
        else:
            if args != ():
                raise TypeError(
                    'No positional arguments should be passed to '
                    f'{self.__class__.__name__}.__init__()'
                )
            if 'value' in kwargs:
                raise TypeError(
                    '"value" keyword argument should not be passed to '
                    f'{self.__class__.__name__}.__init__()'
                )

            self._init_decorator_with_arguments(**kwargs)

    def _init_decorator_without_arguments(self, fget: Callable):
        super().__init__()
        self.__call__(fget)

    def _init_decorator_with_arguments(self, **kwargs):
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

    def __get__(
        self, owner: Optional['Settings'], owner_type=None
    ) -> Union[Any, 'Setting']:
        # == class-level access ==
        if not owner:
            return self

        if self.fget is None:
            raise AttributeError("Unreadable attribute")

        return self.get_value(owner)

    def get_value(self, owner: 'Settings'):
        return self.fget(owner)

    def __set__(self, owner: 'Settings', val):
        raise AttributeError("Can't set attribute: property setting cannot be set")
