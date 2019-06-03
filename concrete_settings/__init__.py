import sys

from .concrete_settings import (
    Settings,
    Setting,
    OverrideSetting,
    PropertySetting,
    universal_behavior,
)

setting = PropertySetting

name = "concrete_settings"
PY_VERSION = (sys.version_info.major, sys.version_info.minor)
PY_36 = (3, 6)

if PY_VERSION < PY_36:
    raise ImportError("Python 3.6 or higher is required by concrete_settings")
