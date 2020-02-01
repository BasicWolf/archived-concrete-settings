import os
from typing import Any, Tuple, Optional

from concrete_settings.sources import (
    Source,
    StringSourceMixin,
    AnySource,
    register_source,
)


@register_source
class EnvVarSource(StringSourceMixin, Source):
    def __init__(self):
        self.data = os.environ

    @staticmethod
    def get_source(src: AnySource) -> Optional['EnvVarSource']:
        if isinstance(src, EnvVarSource):
            return src
        else:
            return None

    def read(self, setting, parents: Tuple[str, ...] = ()) -> Any:
        parents_upper = map(str.upper, parents)
        key = '_'.join((*parents_upper, setting.name))
        val = os.environ[key]
        return self.convert_value(val, setting.type_hint)
