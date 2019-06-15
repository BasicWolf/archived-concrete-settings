import pytest

from concrete_settings import Settings, Setting, Undefined, setting, required, override
from concrete_settings.concrete_settings import SettingBehavior, deprecated
from concrete_settings.exceptions import SettingsValidationError, SettingsStructureError


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
        def __init__(self, summand):
            self.summand = summand

        def get_setting_value(self, setting, owner, get_value):
            return get_value() + self.summand

    return Plus


# == SettingsBehavior == #


def test_setting_behavior_get():
    get_was_called = False

    class B(SettingBehavior):
        def get_setting_value(self, setting, owner, get_value):
            nonlocal get_was_called
            get_was_called = True
            return get_value()

    class S(Settings):
        D = Setting(10) @ B()

    assert S().D == 10
    assert get_was_called


def test_setting_behavior_set():
    set_was_called = False

    class B(SettingBehavior):
        def set_setting_value(self, setting, owner, val, set_value):
            nonlocal set_was_called
            set_was_called = True
            set_value(val)

    class S(Settings):
        D = Setting(10) @ B()

    s = S()
    s.D = 20
    assert s.D == 20
    assert set_was_called


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
        @setting
        def D(self):
            return 30

    assert S().D == 6


def test_setting_behavior_with_property_setting_order(div, plus):
    class S(Settings):
        @div(2)
        @plus(5)
        @setting
        def D(self):
            return 15

    assert S().D == 10

    class S(Settings):
        @div(5)
        @plus(2)
        @setting
        def D(self):
            return 18

    assert S().D == 4


# == Deprecated == #


def test_deprecated_warns_when_validating():
    class S(Settings):
        D = 10 @ deprecated

    with pytest.warns(DeprecationWarning):
        S().is_valid()


def test_deprecated_warning_message():
    class S(Settings):
        D = 10 @ deprecated()

    with pytest.warns(
        DeprecationWarning,
        match=r"Setting `D` in class `<class 'tests.test_behaviors.test_deprecated_warning_message.<locals>.S'>` is deprecated.",
    ) as w:
        S().is_valid()
        assert len(w) == 1


def test_deprecated_error_when_validating():
    class S(Settings):
        D = 10 @ deprecated(error_on_validation=True)

    with pytest.raises(SettingsValidationError):
        S().is_valid(raise_exception=True)


def test_deprecated_warns_on_get():
    class S(Settings):
        D = 10 @ deprecated(warn_on_get=True)

    with pytest.warns(DeprecationWarning):
        S().D


def test_deprecated_warns_on_set():
    class S(Settings):
        D = 10 @ deprecated(warn_on_set=True)

    with pytest.warns(DeprecationWarning):
        S().D = 20


def test_deprecated_not_warns():
    class S(Settings):
        D = 10 @ deprecated(warn_on_validation=False)

    with pytest.warns(None):
        S().is_valid()
        S().D
        S().D = 20


def test_deprecated_on_property_setting():
    class S(Settings):
        @deprecated
        @setting
        def D(self):
            return 30

    with pytest.warns(DeprecationWarning):
        assert S().is_valid()


# == required == #


def test_required():
    class S(Settings):
        default_validators = ()

        D = Undefined @ required

    with pytest.raises(
        SettingsValidationError, match="Setting `D` is required to have a value."
    ):
        S().is_valid(raise_exception=True)


def test_required_setting_has_value_does_not_raise_exception():
    class S(Settings):
        default_validators = ()

        D = 10 @ required

    assert S().is_valid()


# == override == #
def test_validate_override_smoke(v_int, v_str):
    class S(Settings):
        T: int = v_int

    class S1(S):
        T: str = v_str @ override

    s1 = S1()
    s1.is_valid()
    assert s1.T == v_str


def test_structure_error_without_override(v_int, v_str):
    class S(Settings):
        T: int = v_int

    class S1(S):
        T: str = v_str

    with pytest.raises(SettingsStructureError) as e:
        S1()
    e.match('types differ')
