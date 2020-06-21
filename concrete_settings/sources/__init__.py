from pathlib import Path
from typing import Any, Dict, List, Tuple, Type, Optional, Union
from typing import TYPE_CHECKING

from ..exceptions import ConcreteSettingsError
from . import strategies  # noqa: F401 # imported but unused

if TYPE_CHECKING:
    from ..settings import Setting


_registered_sources = set()

AnySource = Union[Dict[str, Any], str, 'Source', Path]


class NotFound:
    pass


def register_source(source_cls: Type['Source']):
    global _registered_sources
    _registered_sources.add(source_cls)
    return source_cls


class NoSuitableSourceFound(ConcreteSettingsError):
    def __init__(self, src: AnySource):
        super().__init__(
            f'No suitable source found to handle "{src}".\n'
            'Perhaps you have forgotten to register the source?'
        )


def get_source(src: AnySource) -> 'Source':
    if isinstance(src, Source):
        return src

    for src_cls in _registered_sources:
        source = src_cls.get_source(src)
        if source is not None:
            return source

    raise NoSuitableSourceFound(src)


class Source:
    @staticmethod
    def get_source(src: AnySource) -> Optional['Source']:
        return None

    def read(
        self, setting: 'Setting', parents: Tuple[str, ...] = ()
    ) -> Union[Type[NotFound], Any]:
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
    def get_source(src: AnySource) -> Optional['DictSource']:
        if isinstance(src, dict):
            return DictSource(src)
        elif isinstance(src, DictSource):
            return src
        else:
            return None

    def read(
        self, setting: 'Setting', parents: Tuple[str, ...] = ()
    ) -> Union[Type[NotFound], Any]:
        d = self.data
        for key in parents:
            d = d[key]

        val = d.get(setting.name, NotFound)
        return val


class FileSource(Source):
    extensions: List[str] = []

    path: str

    def __init__(self, path):
        self.path = path

    @classmethod
    def get_source(cls, src) -> Optional['FileSource']:
        if isinstance(src, cls):
            return src

        if isinstance(src, Path):
            src = str(src.resolve())

        if isinstance(src, str):
            for ext in cls.extensions:
                if src.endswith(ext):
                    return cls(src)

        return None
