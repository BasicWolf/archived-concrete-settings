class ConcreteSettingsError(Exception):
    """Base class for all concrete_settings exceptions."""
    pass


class SettingDiffersError(ConcreteSettingsError):
    pass

class SettingsNotValidatedError(ConcreteSettingsError):

    def __init__(self, cls_name, setting_name):
        super().__init__(
            f"Cannot access setting {setting_name}: an instance of {cls_name} "
            "has not been validated."
        )
