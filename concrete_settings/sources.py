import os
from typing import Type, Union, Any, Dict, Tuple

from .exceptions import ConcreteSettingsError

_registered_sources = set()

TAnySource = Union[Dict[str, Any], str, 'Source']
CannotHandle = object()


def register_source(source_cls: Type['Source']):
    global _registered_sources
    _registered_sources.add(source_cls)
    return source_cls


class NoSuitableSourceFoundError(ConcreteSettingsError):
    def __init__(self, src: TAnySource):
        super().__init__(f'No suitable source found to handle "{src}"')


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
    def get_source(src: TAnySource) -> bool:
        return CannotHandle

    def read(self, name, parents: Tuple[str] = ()) -> Any:
        pass


@register_source
class DictSource(Source):
    def __init__(self, s: dict):
        self.data: dict = s

    @staticmethod
    def get_source(s: TAnySource) -> bool:
        if isinstance(s, dict):
            return DictSource(s)
        else:
            return CannotHandle

    def read(self, name, parents: Tuple[str] = ()) -> Any:
        d = self.data
        for key in parents:
            d = d[key]

        val = d[name]
        return val


class EnvVarSource(Source):
    def __init__(self):
        self.data = os.environ

    @staticmethod
    def get_source(src: TAnySource) -> bool:
        if isinstance(src, EnvVarSource):
            return src
        else:
            return CannotHandle

    def read(self, name, parents: Tuple[str] = ()) -> Any:
        parents_upper = map(str.upper, parents)
        key = (*parents_upper, name).join('_')
        val = os.environ[key]
        return val
