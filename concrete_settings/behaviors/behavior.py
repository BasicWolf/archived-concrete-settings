import types
from typing import Any, Union

from ..settings import Setting, PropertySetting, Settings


class GenericBehaviorMeta(type):
    def __call__(cls, *args, init_with_arguments=False, **kwargs):
        # Explicitly tell the metaclass that
        # Behavior.__init__(arg1, arg2, ...)
        # is expected
        # Case: @validate(validator1, ...)

        if init_with_arguments:
            return super().__call__(*args, **kwargs)

        # Act as a decorator
        _decorating_setting_or_method = (
            len(args) == 1
            and len(kwargs) == 0
            and isinstance(args[0], (Setting, types.FunctionType))
        )

        if _decorating_setting_or_method:
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
        if not isinstance(setting, Setting):
            setting = Setting(setting)

        bhv = cls()
        return bhv(setting)


class BehaviorWithArgumentsMeta(GenericBehaviorMeta):
    def __call__(cls, *args, **kwargs):
        return super().__call__(*args, **kwargs, init_with_arguments=True)


class Behavior(metaclass=GenericBehaviorMeta):
    def __call__(self, setting_or_method: Union[Setting, types.FunctionType]):
        setting: Setting

        if isinstance(setting_or_method, types.FunctionType):
            setting = PropertySetting(setting_or_method)
        else:
            setting = setting_or_method
        # Act as a decorator
        self.decorate(setting)
        return setting

    def __rmatmul__(self, setting: Any):
        if not isinstance(setting, Setting):
            setting = Setting(setting)

        self.decorate(setting)
        return setting

    def decorate(self, setting: Setting):
        pass


class GetterSetterBehavior(Behavior):
    def decorate(self, setting: Setting):
        # replace setting.get_value and .set_value by
        # corresponding behavior methods
        self._setting_get_value = setting.get_value
        self._setting_set_value = setting.set_value
        setting.get_value = types.MethodType(self.get_value, setting)  # type: ignore
        setting.set_value = types.MethodType(self.set_value, setting)  # type: ignore
        super().decorate(setting)

    def get_value(self, setting: Setting, owner: Settings) -> Any:
        return self._setting_get_value(owner)

    def set_value(self, setting: Setting, owner: Settings, value):
        self._setting_set_value(owner, value)
