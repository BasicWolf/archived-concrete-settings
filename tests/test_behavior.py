import pytest

from concrete_settings import (
    Settings,
    Setting,
    setting as property_setting,
    Behaviors,
    SettingBehavior,
    override,
)
from concrete_settings.exceptions import StructureError


@pytest.fixture
def div():
    class Div(SettingBehavior):
        def __init__(self, divisor=2):
            self.divisor = divisor

        def get_setting_value(self, setting, owner, get_value):
            return get_value() / self.divisor

    return Div


@pytest.fixture
def plus():
    class Plus(SettingBehavior):
        def __init__(self, addend):
            self.addend = addend

        def get_setting_value(self, setting, owner, get_value):
            return get_value() + self.addend

    return Plus


@pytest.fixture
def setting_behavior_mock():
    class SettingBehaviorMock(SettingBehavior):
        get_setting_value_was_called = False
        set_setting_value_was_called = False

        def get_setting_value(self, setting, owner, get_value):
            self.get_setting_value_was_called = True
            return get_value()

        def set_setting_value(self, setting, owner, val, set_value):
            self.set_setting_value_was_called = True
            set_value(val)

    return SettingBehaviorMock


# == SettingsBehavior == #


def test_setting_behavior_get(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()

    class S(Settings):
        D = Setting(10) @ bhv_mock

    assert S().D == 10
    assert bhv_mock.get_setting_value_was_called


def test_setting_behavior_set(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()

    class S(Settings):
        D = Setting(10) @ bhv_mock

    s = S()
    s.D = 20
    assert s.D == 20
    assert bhv_mock.set_setting_value_was_called


def test_universal_constructor_matmul_on_right_side(div):
    class S(Settings):
        D = Setting(10) @ div
        E = Setting(9) @ div(3)

    assert S().D == 5
    assert S().E == 3


def test_universal_constructor_value_on_left_side(div):
    class S(Settings):
        D = 10 @ div
        E = 9 @ div(3)

    assert S().D == 5
    assert S().E == 3


def test_setting_behavior_call_order(div, plus):
    class S(Settings):
        D = Setting(23) @ plus(2) @ div(5)

    s = S()
    assert s.D == 5

    class S(Settings):
        D = Setting(25) @ div(5) @ plus(2)

    s = S()
    assert s.D == 7


def test_setting_behavior_with_property_setting(div):
    class S(Settings):
        @div(5)
        @property_setting
        def D(self):
            return 30

    assert S().D == 6


def test_setting_behavior_with_property_setting_order(div, plus):
    class S(Settings):
        @div(2)
        @plus(5)
        @property_setting
        def D(self):
            return 15

    assert S().D == 10

    class S(Settings):
        @div(5)
        @plus(2)
        @property_setting
        def D(self):
            return 18

    assert S().D == 4


# Behaviors


def test_behaviors_injecting_item_increases_length(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()
    behaviors = Behaviors()
    behaviors.inject(bhv_mock)

    assert len(behaviors) == 1


def test_behaviors_injected_item_can_be_get_by_index(setting_behavior_mock):
    bhv_mock = setting_behavior_mock()
    behaviors = Behaviors()
    behaviors.inject(bhv_mock)

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
    behaviors.inject(bhv_mock)

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
    behaviors.inject(bhv_mock)

    behaviors.set_setting_value(MySettings.SOME_SETTING, settings, 20, set_value)

    assert set_value_called_with_val == 20
    assert bhv_mock.set_setting_value_was_called


# == override == #
def test_validate_override():
    class BaseSettings(Settings):
        AGE: int = 10

    class DevSettings(BaseSettings):
        AGE: str = 'old' @ override

    s1 = DevSettings()
    assert s1.is_valid()
    assert s1.AGE == 'old'


def test_structure_error_without_override():
    class S(Settings):
        T: int = 10

    class S1(S):
        T: str = 'abc'

    with pytest.raises(StructureError) as e:
        S1()
    e.match('types differ')


def test_override_on_property_setting():
    class S(Settings):
        T: int = 10

    class S1(S):
        @override
        @property_setting
        def T(self) -> str:
            return 'abc'

    s1 = S1()
    assert s1.is_valid()
    assert s1.T == 'abc'


def test_structure_error_without_override_on_property_setting():
    class S(Settings):
        T: int = 10

    class S1(S):
        @property_setting
        def T(self) -> str:
            return 'abc'

    with pytest.raises(StructureError):
        S1()
