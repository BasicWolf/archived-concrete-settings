from enum import Enum
from typing import Type, Union, Any, Dict, Tuple, List

from .exceptions import ConcreteSettingsError

_registered_sources = set()

TAnySource = Union[Dict[str, Any], str, 'Source']


class CannotHandleType(Enum):
    token = 0


CannotHandle = CannotHandleType.token


def register_source(source_cls: Type['Source']):
    global _registered_sources
    _registered_sources.add(source_cls)
    return source_cls


class NoSuitableSourceFoundError(ConcreteSettingsError):
    def __init__(self, src: TAnySource):
        super().__init__(
            f'No suitable source found to handle "{src}".'
            'Perhaps you have forgotten to register the source?'
        )


def get_source(src: TAnySource) -> 'Source':
    if isinstance(src, Source):
        return src

    for src_cls in _registered_sources:
        source = src_cls.get_source(src)
        if source is not CannotHandle:
            return source

    raise NoSuitableSourceFoundError(src)


class Source:
    @staticmethod
    def get_source(src: TAnySource) -> Union['Source', CannotHandleType]:
        return CannotHandle

    def read(self, setting, parents: Tuple[str] = ()) -> Any:
        pass


class StringSourceMixin:
    """Extends source by providing a string value to required type
       conversion method."""

    @staticmethod
    def convert_value(val: str, type_hint: Any = None) -> Any:
        """Convert given string value to type based on `type_hint`"""
        if type_hint in (int, float):
            return type_hint(val)
        elif type_hint is bool:
            if val.lower() == 'true':
                return True
            elif val.lower() == 'false':
                return False

        return val


@register_source
class DictSource(Source):
    def __init__(self, s: dict):
        self.data: dict = s

    @staticmethod
    def get_source(src: TAnySource) -> Union['DictSource', CannotHandleType]:
        if isinstance(src, dict):
            return DictSource(src)
        elif isinstance(src, DictSource):
            return src
        else:
            return CannotHandle

    def read(self, setting, parents: Tuple[str] = ()) -> Any:
        d = self.data
        for key in parents:
            d = d[key]

        val = d[setting.name]
        return val


class FileSource(Source):
    extensions: List[str] = []

    path: str

    def __init__(self, path):
        self.path = path

    @classmethod
    def get_source(cls, src) -> Union['FileSource', CannotHandleType]:
        if isinstance(src, cls):
            return src
        elif isinstance(src, str):
            for ext in cls.extensions:
                if src.endswith(ext):
                    return cls(src)

        return CannotHandle
