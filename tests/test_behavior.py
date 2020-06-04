import pytest

from concrete_settings import (
    Settings,
    Setting,
    setting as property_setting,
    Behavior,
    override,
)
from concrete_settings.exceptions import StructureError


@pytest.fixture
def div():
    class Div(Behavior):
        def __init__(self, divisor=2):
            self.divisor = divisor

        def get_value(self, setting, owner):
            return super().get_value(setting, owner) / self.divisor

    return Div


@pytest.fixture
def plus():
    class Plus(Behavior):
        def __init__(self, addend):
            self.addend = addend

        def get_value(self, setting, owner):
            return super().get_value(setting, owner) + self.addend

    return Plus


@pytest.fixture
def setting_behavior_mock():
    class BehaviorMock(Behavior):
        get_value_was_called = False
        set_value_was_called = False

        def get_value(self, setting, owner):
            self.get_value_was_called = True
            return super().get_value(setting, owner)

        def set_value(self, setting, owner, value):
            self.set_value_was_called = True
            super().set_value(setting, owner, value)

    return BehaviorMock


# == SettingsBehavior == #


def test_setting_behavior_get(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()

    class TestSettings(Settings):
        MAX_SPEED = Setting(10) @ bhv_mock

    assert TestSettings().MAX_SPEED == 10
    assert bhv_mock.get_value_was_called


def test_setting_behavior_set(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()

    class TestSettings(Settings):
        MAX_SPEED = Setting(10) @ bhv_mock

    test_settings = TestSettings()
    test_settings.MAX_SPEED = 20
    assert test_settings.MAX_SPEED == 20
    assert bhv_mock.set_value_was_called


def test_universal_constructor_matmul_on_right_side(div):
    class TestSettings(Settings):
        MAX_SPEED = Setting(10) @ div
        MIN_SPEED = Setting(9) @ div(3)

    assert TestSettings().MAX_SPEED == 5
    assert TestSettings().MIN_SPEED == 3


def test_universal_constructor_value_on_left_side(div):
    class TestSettings(Settings):
        MAX_SPEED = 10 @ div
        MIN_SPEED = 9 @ div(3)

    assert TestSettings().MAX_SPEED == 5
    assert TestSettings().MIN_SPEED == 3


def test_setting_behavior_call_order(div, plus):
    class TestSettings(Settings):
        MAX_SPEED = Setting(23) @ plus(2) @ div(5)

    test_settings = TestSettings()
    assert test_settings.MAX_SPEED == 5

    class TestSettings(Settings):
        MAX_SPEED = Setting(25) @ div(5) @ plus(2)

    test_settings = TestSettings()
    assert test_settings.MAX_SPEED == 7


def test_setting_behavior_with_explicit_property_setting(div):
    class TestSettings(Settings):
        @div(5)
        @property_setting
        def MICE_COUNT(self):
            return 30

    assert TestSettings().MICE_COUNT == 6


def test_setting_behavior_with_implicit_property_setting(div):
    class TestSettings(Settings):
        @div(5)
        def MICE_COUNT(self):
            return 30

    assert TestSettings().MICE_COUNT == 6


def test_setting_behavior_with_property_setting_order(div, plus):
    class MiceSettings(Settings):
        @div(2)
        @plus(5)
        @property_setting
        def MICE_COUNT(self):
            return 15

    assert MiceSettings().MICE_COUNT == 10

    class HamsterSettings(Settings):
        @div(5)
        @plus(2)
        @property_setting
        def HAMSTER_COUNT(self):
            return 18

    assert HamsterSettings().HAMSTER_COUNT == 4


# == override == #
def test_validate_override():
    class BaseSettings(Settings):
        AGE: int = 10

    class DevSettings(BaseSettings):
        AGE: str = 'old' @ override

    dev_settings = DevSettings()
    assert dev_settings.is_valid()
    assert dev_settings.AGE == 'old'


def test_structure_error_without_override():
    class BaseSettings(Settings):
        AGE: int = 10

    class DevSettings(BaseSettings):
        AGE: str = 'old'

    with pytest.raises(StructureError) as e:
        DevSettings()
    e.match('types differ')


def test_override_on_property_setting():
    class BaseSettings(Settings):
        MAX_SPEED: int = 10

    class DevSettings(BaseSettings):
        @override
        @property_setting
        def MAX_SPEED(self) -> str:
            return 'abc'

    dev_settings = DevSettings()
    assert dev_settings.is_valid()
    assert dev_settings.MAX_SPEED == 'abc'


def test_structure_error_without_override_on_property_setting():
    class BaseSettings(Settings):
        MAX_SPEED: int = 10

    class DevSettings(BaseSettings):
        @property_setting
        def MAX_SPEED(self) -> str:
            return 'abc'

    with pytest.raises(StructureError):
        DevSettings()
