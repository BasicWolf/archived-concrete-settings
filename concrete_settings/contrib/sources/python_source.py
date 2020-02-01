import importlib.util
from pathlib import Path
from typing import Any, Tuple

from concrete_settings.sources import FileSource, register_source


@register_source
class PythonSource(FileSource):
    extensions = ['.py']

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
    def _read_file(path: str):
        module_name = Path(path).stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        return vars(module)
