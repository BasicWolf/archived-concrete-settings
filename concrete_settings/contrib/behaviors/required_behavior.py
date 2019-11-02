from concrete_settings.behaviors import SettingBehavior
from concrete_settings.validators import RequiredValidator


class required(SettingBehavior):
    def __init__(self, message='Setting `{name}` is required to have a value.'):
        self.message = message

    def inject(self, setting):
        setting.validators = (RequiredValidator(self.message),) + setting.validators
        return super().inject(setting)
