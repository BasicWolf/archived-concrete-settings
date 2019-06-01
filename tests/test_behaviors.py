import pytest

from concrete_settings.behaviors import (
    deprecated,
    SettingBehavior,
    generic_behavior_init,
)
from concrete_settings.exceptions import SettingsValidationError

from concrete_settings import Settings, Setting, setting


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


def test_setting_behavior_call_order():
    class Div(SettingBehavior):
        def __init__(self, divisor):
            self.divisor = divisor

        def get_setting_value(self, setting, owner, get_value):
            return get_value() / self.divisor

    class S(Settings):
        D = Setting(100) @ Div(2) @ Div(5)

    s = S()
    assert s.D == 10


# def test_generic_behavior_init_with_default_args():
#     class bhv(SettingBehavior):
#         @generic_behavior_init
#         def __init__(self, x='I am X'):
#             self.x = x

#     class S(Settings):
#         @bhv
#         @setting
#         def D(self):
#             return getattr(type(self), 'D').x

#     assert S().D == 'I am x'


# == Deprecated == #


def test_deprecated_warns_when_validating():
    class S(Settings):
        D = Setting(10) @ deprecated()

    with pytest.warns(DeprecationWarning):
        S().is_valid()


def test_deprecated_warning_message():
    class S(Settings):
        D = Setting(10) @ deprecated()

    with pytest.warns(
        DeprecationWarning,
        match=r"Setting `D` in class `<class 'tests.test_behaviors.test_deprecated_warning_message.<locals>.S'>` is deprecated.",
    ) as w:
        S().is_valid()
        assert len(w) == 1


def test_deprecated_error_when_validating():
    class S(Settings):
        D = Setting(10) @ deprecated(error_on_validation=True)

    with pytest.raises(SettingsValidationError):
        S().is_valid(raise_exception=True)


def test_deprecated_warns_on_get():
    class S(Settings):
        D = Setting(10) @ deprecated(warn_on_get=True)

    with pytest.warns(DeprecationWarning):
        S().D


def test_deprecated_warns_on_set():
    class S(Settings):
        D = Setting(10) @ deprecated(warn_on_set=True)

    with pytest.warns(DeprecationWarning):
        S().D = 20


def test_deprecated_not_warns():
    class S(Settings):
        D = Setting(10) @ deprecated(warn_on_validation=False)

    with pytest.warns(None):
        S().is_valid()
        S().D
        S().D = 20
