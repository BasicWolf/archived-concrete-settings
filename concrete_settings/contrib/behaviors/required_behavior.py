from concrete_settings import Behavior
from concrete_settings.validators import RequiredValidator


class required(Behavior):
    def __init__(self, message: str = None):
        self.message = message

    def inject(self, setting):
        setting.validators = (RequiredValidator(self.message),) + setting.validators
        return super().inject(setting)
