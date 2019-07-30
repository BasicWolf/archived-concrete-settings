from typing import Type, Union, Any, Dict

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
    for src_cls in _registered_sources:
        source = src_cls.get_source(src)
        if source is not CannotHandle:
            return source

    raise NoSuitableSourceFoundError(src)


class Source:
    @staticmethod
    def get_source(src: TAnySource) -> bool:
        return CannotHandle

    def read(self) -> dict:
        pass


class DummySource(Source):
    """"""

    def get_source(src: TAnySource) -> bool:
        return DummySource()

    def read(self) -> dict:
        return {}


@register_source
class DictSource(Source):
    def __init__(self, s: TAnySource):
        self.data: dict = s

    @staticmethod
    def get_source(s: TAnySource) -> bool:
        if isinstance(s, dict):
            return DictSource(s)
        else:
            return CannotHandle

    def read(self) -> dict:
        return self.data
