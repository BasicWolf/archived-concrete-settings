import warnings
from typing import TYPE_CHECKING, Any

from concrete_settings.behaviors.behavior import GetterSetterBehavior
from concrete_settings.contrib.validators import DeprecatedValidator

if TYPE_CHECKING:
    from concrete_settings import Setting, Settings


class deprecated(GetterSetterBehavior):
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

    def decorate(self, setting: 'Setting'):
        if self.warn_on_validation or self.error_on_validation:
            setting.validators = (
                DeprecatedValidator(self.deprecation_message, self.error_on_validation),
            ) + setting.validators
        super().decorate(setting)

    def get_value(self, setting: 'Setting', owner: 'Settings') -> Any:
        if self.warn_on_get:
            if owner and not owner.is_being_validated:
                msg = self.deprecation_message.format(owner=owner, name=setting.name)
                warnings.warn(msg, DeprecationWarning)
        return super().get_value(setting, owner)

    def set_value(self, setting: 'Setting', owner: 'Settings', value):
        if self.warn_on_set:
            if not owner.is_being_validated:
                msg = self.deprecation_message.format(owner=owner, name=setting.name)
                warnings.warn(msg, DeprecationWarning)
        super().set_value(setting, owner, value)
