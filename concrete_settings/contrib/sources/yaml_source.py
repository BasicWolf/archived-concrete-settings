from typing import Any, Tuple

from concrete_settings.exceptions import ConcreteSettingsError
from concrete_settings.sources import FileSource, register_source


@register_source
class YamlSource(FileSource):
    extensions = ['.yml', '.yaml']

    def __init__(self, path):
        try:
            import yaml  # noqa: F401 # imported but unused
        except ImportError as e:
            raise ConcreteSettingsError(
                f'YAML source is not available for `{path}` '
                'due to error importing `yaml` package.\n'
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
