import functools
import types
import typing
import warnings

from .validators import DeprecatedValidator

if typing.TYPE_CHECKING:
    import concrete_settings


class SettingBehavior:
    def __call__(self, setting: 'concrete_Settings.Setting'):
        return self.inject(setting)

    def __rmatmul__(self, setting: 'concrete_settings.Setting'):
        return self.inject(setting)

    def inject(
        self, setting: 'concrete_settings.Setting'
    ) -> 'concrete_settings.Setting':
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
                return get_value(owner, type(owner))

        return _get_value()

    def set_setting_value(self, setting, owner, val, set_value):
        """Chain and invoke set_setting_value() of each behavior."""

        def _set_value(v, i=0):
            if i < len(self):
                self[i].set_setting_value(
                    setting, owner, v, functools.partial(_set_value, i=i + 1)
                )
            else:
                set_value(owner, v)

        return _set_value(val)


def generic_behavior_init(f_init):
    """Class-decorator's __init__() method wrapper.

    Allows a class-decorator to be invoked on a function/method
    without supplying arguments. In other words:
    make @decorator and @decorator() work likewise."""

    @functools.wraps(f_init)
    def wrapped_init(self, *args, **kwargs):
        assert isinstance(self, SettingBehavior)

        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            f_init(self)
            self.__call__(args[0])
        else:
            f_init(self, *args, **kwargs)

    return wrapped_init


class deprecated(SettingBehavior):
    @generic_behavior_init
    def __init__(
        self,
        deprecation_message: str = 'Setting `{name}` in class `{owner}` is deprecated.',
        *,
        warn_on_validation=True,
        error_on_validation=False,
        warn_on_get=False,
        warn_on_set=False,
    ):
        self.deprecation_message = deprecation_message
        self.error_on_validation = error_on_validation
        self.warn_on_validation = warn_on_validation
        self.warn_on_get = warn_on_get
        self.warn_on_set = warn_on_set

    def inject(self, setting):
        if self.warn_on_validation or self.error_on_validation:
            setting.validators = (
                DeprecatedValidator(self.deprecation_message, self.error_on_validation),
            ) + setting.validators

        return super().inject(setting)

    def get_setting_value(self, setting, owner, get_value):
        if self.warn_on_get:
            if owner and not owner.validating:
                msg = self.deprecation_message.format(owner=owner, name=setting.name)
                warnings.warn(msg, DeprecationWarning)
        return get_value()

    def set_setting_value(self, setting, owner, val, set_value):
        if self.warn_on_set:
            if not owner.validating:
                msg = self.deprecation_message.format(owner=owner, name=setting.name)
                warnings.warn(msg, DeprecationWarning)
        set_value(val)
