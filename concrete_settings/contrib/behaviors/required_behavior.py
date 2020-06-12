from concrete_settings.behaviors import Behavior
from concrete_settings.validators import RequiredValidator


class required(Behavior):
    def __init__(self, message: str = None):
        self.message = message

    def decorate(self, setting):
        setting.validators = (RequiredValidator(self.message),) + setting.validators
        super().decorate(setting)
