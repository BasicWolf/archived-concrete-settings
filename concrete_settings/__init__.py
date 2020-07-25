import sys

from .setting import Setting, PropertySetting  # noqa: F401 # imported but unused
from .settings import (  # noqa: F401 # imported but unused
    Settings,
    INVALID_SETTINGS,
)

from .exceptions import ValidationError  # noqa: F401 # imported but unused
from .validators import Validator  # noqa: F401 # imported but unused
from .types import Undefined  # noqa: F401 # imported but unused
from .sources import register_source  # noqa: F401 # imported but unused
from .contrib.behaviors import required  # noqa: F401 # imported but unused
from .behaviors import (  # noqa: F401 # imported but unused
    Behavior,
    GetterSetterBehavior,
    override,
    validate,
)

# GLOBALS
from .setting_registry import registry  # noqa: F401 # imported but unused

# ALIASES
setting = PropertySetting

name = "concrete_settings"
PY_VERSION = (sys.version_info.major, sys.version_info.minor)
PY_36 = (3, 6)

if PY_VERSION < PY_36:
    raise ImportError("Python 3.6 or higher is required by concrete_settings library")


def _load_contrib():
    from .contrib.sources import YamlSource, JsonSource, EnvVarSource  # noqa: F401


_load_contrib()


__version__ = "0.0.0"
