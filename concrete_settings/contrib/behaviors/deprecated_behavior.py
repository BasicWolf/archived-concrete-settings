import warnings

from concrete_settings.behaviors import SettingBehavior
from concrete_settings.contrib.validators import DeprecatedValidator


class deprecated(SettingBehavior):
    """Adds :class:`DeprecatedValidator <concrete_settings.contrib.validators.DeprecatedValidator>`  # noqa: E501 # line too long
       to the setting."""

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
