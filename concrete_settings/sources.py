import os
from typing import Type, Union, Any, Dict, Tuple, Callable

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

    def read(self, name, parents: Tuple[str] = (), type_hint: Callable = str) -> Any:
        pass


class StringSourceMixin:
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
    def get_source(s: TAnySource) -> bool:
        if isinstance(s, dict):
            return DictSource(s)
        else:
            return CannotHandle

    def read(self, setting, parents: Tuple[str] = ()) -> Any:
        d = self.data
        for key in parents:
            d = d[key]

        val = d[setting.name]
        return val


@register_source
class EnvVarSource(StringSourceMixin, Source):
    def __init__(self):
        self.data = os.environ

    @staticmethod
    def get_source(src: TAnySource) -> bool:
        if isinstance(src, EnvVarSource):
            return src
        else:
            return CannotHandle

    def read(self, setting, parents: Tuple[str] = ()) -> Any:
        parents_upper = map(str.upper, parents)
        key = '_'.join(*parents_upper, setting.name)
        val = os.environ[key]
        return self.convert_value(val, setting.type_hint)
