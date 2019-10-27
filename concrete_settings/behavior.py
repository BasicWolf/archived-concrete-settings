import functools
from typing import NewType, Any


TSetting = NewType('TSetting', 'concrete_settings.Setting')


class SettingBehaviorMeta(type):
    def __call__(self, *args, **kwargs):
        from concrete_settings import Setting

        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], Setting):
            bhv = super().__call__()
            return bhv(args[0])
        else:
            bhv = super().__call__(*args, **kwargs)
            return bhv

    def __rmatmul__(self, setting: Any):
        from concrete_settings import Setting

        if not isinstance(setting, Setting):
            setting = Setting(setting)

        bhv = self()
        return bhv(setting)


class SettingBehavior(metaclass=SettingBehaviorMeta):
    def __call__(self, setting: TSetting):
        return self.inject(setting)

    def __rmatmul__(self, setting: Any):
        from concrete_settings import Setting

        if not isinstance(setting, Setting):
            setting = Setting(setting)

        return self.inject(setting)

    def inject(self, setting: TSetting) -> TSetting:
        setting.behaviors.inject(self)
        return setting

    def get_setting_value(self, setting, owner, get_value):
        return get_value()

    def set_setting_value(self, setting, owner, val, set_value):
        set_value(val)


class Behaviors(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def inject(self, behavior):
        self.insert(0, behavior)

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


class override(SettingBehavior):
    pass
