import pytest

from concrete_settings import Settings, setting
from concrete_settings.exceptions import ValidationError
from concrete_settings.contrib.behaviors import deprecated


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
        match=r"Setting `D` in class `<class 'tests.test_behaviors.test_deprecated."
        "test_deprecated_warning_message.<locals>.S'>` is deprecated.",
    ) as w:
        S().is_valid()
        assert len(w) == 1


def test_deprecated_error_when_validating():
    class S(Settings):
        D = 10 @ deprecated(error_on_validation=True)

    with pytest.raises(ValidationError):
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
