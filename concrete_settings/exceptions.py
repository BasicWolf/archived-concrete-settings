from typing import Union, List, Dict


class ConcreteSettingsError(Exception):
    """Base class for all concrete_settings exceptions."""


class StructureError(ConcreteSettingsError):
    """Raised when an inconsistency in settings inheritance hierarchy is detected."""


SettingName = str

ValidationErrorDetail = Union[
    str, List['ValidationErrorDetail'], Dict[SettingName, 'ValidationErrorDetail']
]


class SettingsValidationError(ConcreteSettingsError):
    """Raised by a setting validator when a setting value is invalid"""

    def __init__(self, detail: ValidationErrorDetail = ''):
        self.detail = detail
        self.sources = []

    def prepend_source(self, source):
        self.sources.insert(0, source)

    def __str__(self):
        detail_str = _format_detail(self.detail)
        if self.sources:
            source = '.'.join(self.sources)
            return f'{source}: {detail_str}'
        else:
            return detail_str


def _format_detail(detail) -> str:
    if isinstance(detail, list):
        return '; '.join(_format_detail(d) for d in detail)
    elif isinstance(detail, dict):
        return '\n'.join(f'{k}: {_format_detail(v)}.' for k, v in detail.items())
    else:
        return str(detail)
