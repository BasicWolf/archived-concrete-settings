import pytest
from concrete_settings.exceptions import SettingsValidationError

from concrete_settings import Settings, Setting, Deprecated

# == Deprecated == #


def test_deprecated_warns_when_validating():
    class S(Settings):
        D = Setting(10) @ Deprecated()

    with pytest.warns(DeprecationWarning):
        S().is_valid()


def test_deprecated_warning_message():
    class S(Settings):
        D = Setting(10) @ Deprecated()

    with pytest.warns(
        DeprecationWarning,
        match=r"Setting `D` in class `<class 'tests.test_behaviors.test_deprecated_warning_message.<locals>.S'>` is deprecated.",
    ) as w:
        S().is_valid()
        assert len(w) == 1


def test_deprecated_error_when_validating():
    class S(Settings):
        D = Setting(10) @ Deprecated(error_on_validation=True)

    with pytest.raises(SettingsValidationError):
        S().is_valid(raise_exception=True)


def test_deprecated_warns_on_get():
    class S(Settings):
        D = Setting(10) @ Deprecated(warn_on_get=True)

    with pytest.warns(DeprecationWarning):
        S().D


def test_deprecated_warns_on_set():
    class S(Settings):
        D = Setting(10) @ Deprecated(warn_on_set=True)

    with pytest.warns(DeprecationWarning):
        S().D = 20


def test_deprecated_not_warns():
    class S(Settings):
        D = Setting(10) @ Deprecated(warn_on_validation=False)

    with pytest.warns(None):
        S().is_valid()
        S().D
        S().D = 20
