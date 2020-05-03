import typing

import pytest

from concrete_settings import (
    Settings,
    setting,
)


def test_method_automatically_converted_to_setting():
    class TestSettings(Settings):
        def MICE_NUMBER(self) -> int:
            """MICE_NUMBER docs"""
            return 10

    assert TestSettings.MICE_NUMBER.__doc__ == "MICE_NUMBER docs"
    assert TestSettings.MICE_NUMBER.validators == tuple()
    assert TestSettings.MICE_NUMBER.type_hint == int
    assert TestSettings().MICE_NUMBER == 10


def test_with_setting_attrs_decorated_method():
    class TestSettings(Settings):
        @setting
        def DECORATED_NUMBER(self) -> int:
            """DECORATED_NUMBER docs"""
            return 10

    assert TestSettings.DECORATED_NUMBER.__doc__ == "DECORATED_NUMBER docs"
    assert TestSettings.DECORATED_NUMBER.validators == tuple()
    assert TestSettings.DECORATED_NUMBER.type_hint == int
    assert TestSettings().DECORATED_NUMBER == 10


def test_no_return_type_hint_set_as_any():
    class TestSettings(Settings):
        @setting
        def ANY_MICE(self):
            return 10

    assert TestSettings.ANY_MICE.type_hint is typing.Any


def test_init_checks_positional_arguments_are_empty():
    with pytest.raises(
        TypeError,
        match='No positional arguments should be passed to PropertySetting.__init__()',
    ):

        class TestSettings(Settings):
            @setting('Markus')
            def ADMIN(self):
                ...


def test_init_checks_value_argument_absence():
    with pytest.raises(
        TypeError,
        match=(
            '"value" keyword argument should not be passed to '
            'PropertySetting.__init__()'
        ),
    ):

        class TestSettings(Settings):
            @setting(value='Markus')
            def ADMIN(self):
                return 'Alex'


def test_with_setting_attrs_defined_as_argument(DummyValidator):
    class TestSettings(Settings):
        @setting(type_hint=int, doc="MICE arg docs", validators=(DummyValidator(),))
        def MICE_COUNT(self):
            return 10

    assert TestSettings.MICE_COUNT.__doc__ == "MICE arg docs"
    assert TestSettings.MICE_COUNT.type_hint == int
    assert len(TestSettings.MICE_COUNT.validators) == 1
    assert isinstance(TestSettings.MICE_COUNT.validators[0], DummyValidator)


def test_property_setting_using_other_settings():
    class TestSettings(Settings):
        MICE_COUNT: int = 10
        MICE_NAME: str = 'alex'

        @setting
        def MICE(self) -> str:
            return f'{self.MICE_COUNT} {self.MICE_NAME}'

    test_settings = TestSettings()
    assert test_settings.is_valid()
    assert test_settings.MICE == '10 alex'


def test_property_setting_cannot_be_set():
    class TestSettings(Settings):
        @setting
        def MICE_READONLY(self):
            return 10

    with pytest.raises(
        AttributeError, match="Can't set attribute: property setting cannot be set"
    ):
        TestSettings().MICE_READONLY = 10


def test_property_setting_is_validated():
    validate_called = False

    def validator(value, **_):
        nonlocal validate_called
        validate_called = True

    class TestSettings(Settings):
        @setting(validators=(validator,))
        def DEBUG(self):
            return True

    assert TestSettings().is_valid()
    assert validate_called
