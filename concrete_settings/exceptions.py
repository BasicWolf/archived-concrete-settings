class ConcreteSettingsError(Exception):
    """Base class for all concrete_settings exceptions."""

    pass


class SettingDiffersError(ConcreteSettingsError):
    def __init__(self, name, cls1, cls2, diff):
        super().__init__(
            f'"{name}" setting in classes {cls1} and {cls2} '
            f'have the following difference(s): {diff}'
        )
        pass


class SettingsNotValidatedError(ConcreteSettingsError):
    def __init__(self, cls_name, setting_name):
        super().__init__(
            f"Cannot access setting {setting_name}: an instance of {cls_name} "
            "has not been validated."
        )
