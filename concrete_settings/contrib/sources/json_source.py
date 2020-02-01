import json

from typing import Any, Tuple

from concrete_settings.exceptions import ConcreteSettingsError
from concrete_settings.sources import FileSource, register_source


@register_source
class JsonSource(FileSource):
    extensions = ['.json']

    def __init__(self, path):
        super().__init__(path)
        self._data = None

    def read(self, setting, parents: Tuple[str, ...] = ()) -> Any:
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
