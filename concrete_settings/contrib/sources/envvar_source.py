import os
from typing import Any, Tuple, Union

from concrete_settings.sources import (
    CannotHandle,
    CannotHandleType,
    Source,
    StringSourceMixin,
    TAnySource,
    register_source,
)


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
        key = '_'.join((*parents_upper, setting.name))
        val = os.environ[key]
        return self.convert_value(val, setting.type_hint)
