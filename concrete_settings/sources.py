import os
import json
from typing import Type, Union, Any, Dict, Tuple, Callable

from .exceptions import ConcreteSettingsError

_registered_sources = set()

TAnySource = Union[Dict[str, Any], str, 'Source']


class CannotHandle:
    pass


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
    def get_source(src: TAnySource) -> Union['Source', CannotHandle]:
        return CannotHandle

    def read(self, name, parents: Tuple[str] = (), type_hint: Callable = str) -> Any:
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
    def get_source(src: TAnySource) -> Union['DictSource', CannotHandle]:
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


@register_source
class EnvVarSource(StringSourceMixin, Source):
    def __init__(self):
        self.data = os.environ

    @staticmethod
    def get_source(src: TAnySource) -> Union['EnvVarSource', CannotHandle]:
        if isinstance(src, EnvVarSource):
            return src
        else:
            return CannotHandle

    def read(self, setting, parents: Tuple[str] = ()) -> Any:
        parents_upper = map(str.upper, parents)
        key = '_'.join(*parents_upper, setting.name)
        val = os.environ[key]
        return self.convert_value(val, setting.type_hint)


class FileSource(Source):
    extensions = []

    def __init__(self, path):
        self.path = path
        self.data = {}
        self._read_file()

    def _read_file(self):
        try:
            with open(self.path) as f:
                raw_data = f.read()
                self.data = json.loads(raw_data)
        except FileNotFoundError as e:
            raise ConcreteSettingsError(f"Source file {self.path} was not found") from e
        except json.decoder.JSONDecodeError as e:
            raise ConcreteSettingsError(f"Error parsing JSON from {self.path}: {e}") from e

    def read(self, setting, parents: Tuple[str] = ()) -> Any:
        d = self.data
        for key in parents:
            d = d[key]

        val = d[setting.name]
        return val

    @classmethod
    def get_source(cls, src) -> Union['JsonSource', CannotHandle]:
        if isinstance(src, str):
            for ext in cls.extensions:
                if src.endswith(ext):
                    return JsonSource(src)

        if isinstance(src, JsonSource):
            return src

        return CannotHandle


@register_source
class JsonSource(FileSource):
    extensions = ['.json']


@register_source
class YamlSource(FileSource):
    extensions = ['.yml', '.yaml']

    def __init__(self, path):
        try:
            import yaml
        except ImportError:
            raise ConcreteSettingError(
                f'YAML source is not available for `{path}` due to error importing `yaml` package.\n'
                'Perhaps you have forgotten to install PyYAML?'
            )

        super().__init__(path)
