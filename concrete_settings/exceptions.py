from typing import Union, List, Dict


class ConcreteSettingsError(Exception):
    """Base class for all concrete_settings exceptions."""


class StructureError(ConcreteSettingsError):
    """Raised when an inconsistency in settings inheritance hierarchy is detected."""


SettingName = str

# fmt: off
# type ignored due to cyclic definition, promised to be fixed in
# future mypy versions

#:
ValidationErrorDetails = Union[                   # type: ignore
    str,
    List['ValidationErrorDetails'],               # type: ignore
    Dict[SettingName, 'ValidationErrorDetails'],  # type: ignore
]
# fmt: on


class ValidationError(ConcreteSettingsError):
    sources: List[str]

    def __init__(self, details: ValidationErrorDetails = ''):
        self.details = details
        self.sources = []

    def prepend_source(self, source):
        self.sources.insert(0, source)

    def __str__(self):
        detail_str = _format_detail(self.details)
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
