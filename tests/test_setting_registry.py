import pytest

from concrete_settings import Setting, Settings, registry as global_setting_registry
from concrete_settings.setting_registry import SettingRegistry


@pytest.fixture
def registry():
    return SettingRegistry()


@pytest.fixture
def MyIntSetting():
    class MyIntSetting(Setting):
        pass

    old_int_setting_class = global_setting_registry.get_setting_class_for_type(int)
    global_setting_registry.register_setting(int, MyIntSetting)
    yield MyIntSetting
    # restore
    global_setting_registry.register_setting(int, old_int_setting_class)


def test_setting_type_returned(registry):
    class MyFloatSetting(Setting):
        pass
    registry.register_setting(float, MyFloatSetting)

    assert registry.get_setting_class_for_type(float) is MyFloatSetting


def test_default_setting_type_returned(registry):
    assert registry.get_setting_class_for_type(float) is Setting


def test_registered_setting_type_applied(MyIntSetting):
    class AppSettings(Settings):
        AGE: int = 10

    assert isinstance(AppSettings.AGE, MyIntSetting)


def test_registered_setting_type_not_applied_for_explicit_setting(MyIntSetting):
    class AppSettings(Settings):
        AGE: int = Setting(10)

    assert not isinstance(AppSettings.AGE, MyIntSetting)
