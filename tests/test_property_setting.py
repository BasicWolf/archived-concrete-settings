import typing

import pytest

from concrete_settings import (
    Settings,
    Setting,
    setting,
)


def test_with_setting_attrs_decorated_method():
    class S(Settings):
        @setting
        def V(self) -> int:
            """V docs"""
            return 10

    assert S.V.__doc__ == "V docs"
    assert S.V.validators == tuple()
    assert S.V.type_hint == int
    s = S()
    assert s.V == 10


def test_no_return_type_hint_set_as_any():
    class S(Settings):
        @setting
        def V(self):
            return 10

    assert S.V.type_hint is typing.Any


def test_init_asserts_first_argument():
    with pytest.raises(
        AssertionError,
        match='No positional arguments should be passed to PropertySetting.__init__()'
    ):
        class TestSettings(Settings):
            @setting('Markus')
            def ADMIN(self):
                return 'Alex'


def test_init_asserts_value_argument():
    with pytest.raises(
        AssertionError,
        match='"value" argument should not be passed to PropertySetting.__init__()'
    ):
        class TestSettings(Settings):
            @setting(value='Markus')
            def ADMIN(self):
                return 'Alex'


def test_with_setting_attrs_defined_as_argument(DummyValidator):
    class S(Settings):
        @setting(type_hint=int, doc="V arg docs", validators=(DummyValidator(),))
        def V(self):
            return 10

    assert S.V.__doc__ == "V arg docs"
    assert S.V.type_hint == int
    assert len(S.V.validators) == 1
    assert isinstance(S.V.validators[0], DummyValidator)


def test_property_setting_using_other_settings():
    class S(Settings):
        A: int = 10
        B: str = 'hello world'

        @setting
        def AB(self) -> str:
            return f'{self.A} {self.B}'

    s = S()
    assert s.is_valid()
    assert s.AB == '10 hello world'


def test_property_setting_cannot_be_set():
    class S(Settings):
        @setting
        def V(self):
            return 10

    with pytest.raises(
        AttributeError, match="Can't set attribute: property setting cannot be set"
    ):
        S().V = 10


def test_setting_is_validated():
    validate_called = False

    def validator(value, **_):
        nonlocal validate_called
        validate_called = True

    class S(Settings):
        T = Setting(10, validators=(validator,))

    assert S().is_valid()
    assert validate_called
