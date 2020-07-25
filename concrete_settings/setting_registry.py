from typing import Dict, Type

from .setting import Setting


class SettingRegistry:
    def __init__(self):
        self._registry: Dict[Type, Type[Setting]] = {}

    def register_setting(self, type_hint: Type, setting_cls: Type[Setting]):
        self._registry[type_hint] = setting_cls

    def get_setting_class_for_type(self, type_hint: Type) -> Type[Setting]:
        return self._registry.get(type_hint, Setting)


registry = SettingRegistry()
