import os
import json
from enum import Enum
from typing import Type, Union, Any, Dict, Tuple, Callable, List

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


@register_source
class EnvVarSource(StringSourceMixin, Source):
    def __init__(self):
        self.data = os.environ

    @staticmethod
    def get_source(src: TAnySource) -> Union['EnvVarSource', CannotHandleType]:
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


@register_source
class JsonSource(FileSource):
    extensions = ['.json']

    def __init__(self, path):
        super().__init__(path)
        self._data = None

    def read(self, setting, parents: Tuple[str] = ()) -> Any:
        if self._data is None:
            self._data = self._read_file(self.path)

        d = self._data
        for key in parents:
            d = d[key]

        val = d[setting.name]
        return val

    @staticmethod
    def _read_file(path):
        try:
            with open(path) as f:
                raw_data = f.read()
                return json.loads(raw_data)
        except FileNotFoundError as e:
            raise ConcreteSettingsError(f"Source file {path} was not found") from e
        except json.decoder.JSONDecodeError as e:
            raise ConcreteSettingsError(f"Error parsing JSON from {path}: {e}") from e


@register_source
class YamlSource(FileSource):
    extensions = ['.yml', '.yaml']

    def __init__(self, path):
        try:
            import yaml  # noqa: F401 # imported but unused
        except ImportError as e:
            raise ConcreteSettingsError(
                f'YAML source is not available for `{path}` due to error importing `yaml` package.\n'
                'Perhaps you have forgotten to install PyYAML?'
            ) from e
        super().__init__(path)
        self._data = None

    def read(self, setting, parents: Tuple[str] = ()) -> Any:
        if self._data is None:
            self._data = self._read_file(self.path)

        d = self._data
        for key in parents:
            d = d[key]

        val = d[setting.name]
        return val

    @staticmethod
    def _read_file(path):
        import yaml

        try:
            with open(path) as f:
                raw_data = f.read()
                return yaml.safe_load(raw_data)
        except FileNotFoundError as e:
            raise ConcreteSettingsError(f"Source file {path} was not found") from e
        except yaml.YAMLError as e:
            raise ConcreteSettingsError(f"Error parsing YAML from {path}: {e}") from e
