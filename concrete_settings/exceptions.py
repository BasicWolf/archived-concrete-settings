from typing import Union


class ConcreteSettingsError(Exception):
    """Base class for all concrete_settings exceptions."""

    pass


class SettingsValidationError(ConcreteSettingsError):
    default_error = 'Invalid settings'

    def __init__(self, errors: Union[dict, list, str] = None):

        if errors is None:
            errors = self.default_errors

        # For validation failures, we may collect many errors together,
        # so the errors should always be coerced to a list if not already.
        if not isinstance(errors, dict) and not isinstance(errors, list):
            errors = [errors]

    def __str__(self):
        return str(self.errors)


class SettingsNotValidatedError(ConcreteSettingsError):
    def __init__(self, cls_name, setting_name):
        super().__init__(
            f"Cannot access setting {setting_name}: an instance of {cls_name} "
            "has not been validated."
        )
