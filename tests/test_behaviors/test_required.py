import pytest

from concrete_settings import Settings, Undefined
from concrete_settings.exceptions import ValidationError
from concrete_settings.contrib.behaviors import required


def test_required_behavior_validation_fails_when_value_is_undefined():
    class MySettings(Settings):
        DEBUG = Undefined @ required

    with pytest.raises(
        ValidationError,
        match="Setting `DEBUG` is required to have a value. "
        "Current value is `Undefined`",
    ):
        MySettings().is_valid(raise_exception=True)


def test_required_behavior_validation_ok_when_value_is_not_undefined():
    class MySettings(Settings):
        DEBUG = True @ required

    assert MySettings().is_valid()
