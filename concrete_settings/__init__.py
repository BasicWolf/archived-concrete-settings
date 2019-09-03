import sys


from .concrete_settings import (  # noqa: F401 # imported but unused
    Settings,
    Setting,
    PropertySetting,
    Undefined,
    COMMON_ERRORS,
)

from .sources import register_source  # noqa: F401 # imported but unused

setting = PropertySetting

name = "concrete_settings"
PY_VERSION = (sys.version_info.major, sys.version_info.minor)
PY_36 = (3, 6)

if PY_VERSION < PY_36:
    raise ImportError("Python 3.6 or higher is required by concrete_settings")
