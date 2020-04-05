import pytest

from concrete_settings import (
    Settings,
    Setting,
    setting as property_setting,
    Behaviors,
    Behavior,
    override,
)
from concrete_settings.exceptions import StructureError


@pytest.fixture
def div():
    class Div(Behavior):
        def __init__(self, divisor=2):
            self.divisor = divisor

        def get_setting_value(self, setting, owner, get_value):
            return get_value() / self.divisor

    return Div


@pytest.fixture
def plus():
    class Plus(Behavior):
        def __init__(self, addend):
            self.addend = addend

        def get_setting_value(self, setting, owner, get_value):
            return get_value() + self.addend

    return Plus


@pytest.fixture
def setting_behavior_mock():
    class BehaviorMock(Behavior):
        get_setting_value_was_called = False
        set_setting_value_was_called = False

        def get_setting_value(self, setting, owner, get_value):
            self.get_setting_value_was_called = True
            return get_value()

        def set_setting_value(self, setting, owner, value, set_value):
            self.set_setting_value_was_called = True
            set_value(value)

    return BehaviorMock


# == SettingsBehavior == #


def test_setting_behavior_get(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()

    class TestSettings(Settings):
        MAX_SPEED = Setting(10) @ bhv_mock

    assert TestSettings().MAX_SPEED == 10
    assert bhv_mock.get_setting_value_was_called


def test_setting_behavior_set(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()

    class TestSettings(Settings):
        MAX_SPEED = Setting(10) @ bhv_mock

    test_settings = TestSettings()
    test_settings.MAX_SPEED = 20
    assert test_settings.MAX_SPEED == 20
    assert bhv_mock.set_setting_value_was_called


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


# Behaviors


def test_behaviors_prepending_behavior_increases_length(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()
    behaviors = Behaviors()
    behaviors.append(bhv_mock)

    assert len(behaviors) == 1


def test_behaviors_prepended_behavior_can_be_get_by_index(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()
    behaviors = Behaviors()
    behaviors.append(bhv_mock)

    assert behaviors[0] == bhv_mock


def test_behavior_get_setting_value_call_chain(setting_behavior_mock):
    class MySettings(Settings):
        SOME_SETTING = 10

    settings = MySettings()

    get_value_called = False

    def get_value():
        nonlocal get_value_called
        get_value_called = True
        return settings.SOME_SETTING

    bhv_mock = setting_behavior_mock()
    behaviors = Behaviors()
    behaviors.append(bhv_mock)

    assert 10 == behaviors.get_setting_value(
        MySettings.SOME_SETTING, settings, get_value
    )

    assert get_value_called
    assert bhv_mock.get_setting_value_was_called


def test_behavior_set_setting_value_call_chain(setting_behavior_mock):
    class MySettings(Settings):
        SOME_SETTING = 10

    settings = MySettings()

    set_value_called_with_val = None

    def set_value(val):
        nonlocal set_value_called_with_val
        set_value_called_with_val = val

    bhv_mock = setting_behavior_mock()
    behaviors = Behaviors()
    behaviors.append(bhv_mock)

    behaviors.set_setting_value(MySettings.SOME_SETTING, settings, 20, set_value)

    assert set_value_called_with_val == 20
    assert bhv_mock.set_setting_value_was_called


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
