class ConcreteSettingsError(Exception):
    """Base class for all concrete_settings exceptions."""


class SettingsStructureError(ConcreteSettingsError):
    """Raised when an inconsistency in settings inheritance hierarchy is detected."""


class SettingsValidationError(ConcreteSettingsError):
    """Raised by a setting validator when a setting value is invalid"""

    def __init__(self, description: str = ''):
        self.description = description
        self.sources = []

    def prepend_source(self, source):
        self.sources.insert(0, source)

    def __str__(self):
        if self.sources:
            source = '.'.join(self.sources)
            return f'{source}: {self.description}'
        else:
            return self.description
