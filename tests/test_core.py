import importlib
import sys
import typing
from collections import namedtuple

import pytest

import concrete_settings
from concrete_settings import INVALID_SETTINGS, Settings, Setting, Undefined, prefix
from concrete_settings.exceptions import ValidationError


def test_init_empty_settings():
    Settings()


def test_import_in_unsupported_python_fails(mocker):
    VersionInfo = namedtuple(
        'version_info', ['major', 'minor', 'micro', 'releaselevel', 'serial']
    )
    unsupported_python_version_info = VersionInfo(3, 5, 0, 'final', 0)

    mocker.patch.object(sys, 'version_info', unsupported_python_version_info)
    with pytest.raises(
        ImportError, match="Python 3.6 or higher is required by concrete_settings"
    ):
        importlib.reload(concrete_settings)


def test_setting_ctor(v_int):
    validators = (lambda x: x,)
    s = Setting(
        v_int, type_hint=int, validators=validators, doc="docstring", behaviors=()
    )

    assert s.value == v_int
    assert s.__doc__ == "docstring"
    assert s.validators is validators
    assert s.type_hint is int
    assert len(s.behaviors) == 0


def test_settings_converted_from_attributes(v_int):
    class TestSettings(Settings):
        DEMO: int = v_int
        demo: str = v_int

    assert isinstance(TestSettings.DEMO, Setting)
    assert TestSettings.__dict__["DEMO"].type_hint is int
    assert isinstance(TestSettings.demo, int)


def test_setting_set(v_int):
    class TestSettings(Settings):
        DEMO: int = v_int

    class DevSettings(Settings):
        DEMO = v_int + 1

    assert TestSettings().DEMO != DevSettings().DEMO


def test_guessed_type():
    class TestSettings(Settings):
        # Numeric types
        BOOLEAN = True
        INT = 10
        FLOAT = 10.0
        COMPLEX = 10 + 10j

        # Sequences
        LIST = list()
        TUPLE = tuple()
        RANGE = range(3)

        # Text, Binary
        STR = "str"
        BYTES = b"abc"

        # set, frozenset, dict
        SET = set()
        FROZENSET = frozenset()
        DICT = dict()

    d = TestSettings.__dict__
    assert d["BOOLEAN"].type_hint is bool
    assert d["INT"].type_hint is int
    assert d["FLOAT"].type_hint is float
    assert d["COMPLEX"].type_hint is complex
    assert d["LIST"].type_hint is list
    assert d["TUPLE"].type_hint is tuple
    assert d["RANGE"].type_hint is range
    assert d["STR"].type_hint is str
    assert d["BYTES"].type_hint is bytes
    assert d["SET"].type_hint is set
    assert d["FROZENSET"].type_hint is frozenset
    assert d["DICT"].type_hint is dict


def test_classmethod_is_not_automatically_converted_setting():
    class TestSettings(Settings):
        @classmethod
        def CLASS_METH(cls):
            return cls

    assert not isinstance(TestSettings.CLASS_METH, Setting)


def test_staticmethod_is_not_automatically_converted_setting():
    class TestSettings(Settings):
        @staticmethod
        def STATIC_METH():
            return

    assert not isinstance(TestSettings.STATIC_METH, Setting)


def test_property_is_not_automatically_converted_setting():
    class TestSettings(Settings):
        @property
        def PROP_BOOLEAN(self):
            return False

    assert not isinstance(TestSettings.PROP_BOOLEAN, Setting)


def test_guess_setting_type_inherits_type_hint():
    class BaseSettings(Settings):
        DEBUG: typing.Optional[bool] = False

    class DevSettings(BaseSettings):
        DEBUG = True

    assert DevSettings.DEBUG.type_hint == BaseSettings.DEBUG.type_hint


def test_validate_smoke():
    class TestSettings(Settings):
        ...

    test_settings = TestSettings()
    test_settings.is_valid()


def test_setting_is_validated():
    validate_called = False

    def validator(value, **_):
        nonlocal validate_called
        validate_called = True

    class TestSettigs(Settings):
        MAX_SPEED = Setting(10, validators=(validator,))

    assert TestSettigs().is_valid()
    assert validate_called


#
# ValueTypeValidator
#


def test_value_type_validator():
    class TestSettings(Settings):
        MAX_SPEED: str = 10

    with pytest.raises(
        ValidationError,
        match="Expected value of type `<class 'str'>` got value of type `<class 'int'>`",
    ):
        TestSettings().is_valid(raise_exception=True)


def test_value_type_validator_with_inheritance():
    class BaseSettings(Settings):
        MAX_SPEED: str = 10

    class DevSettings(BaseSettings):
        MAX_SPEED = 'abc'

    assert DevSettings().is_valid()


def test_value_type_validator_allows_undefined_for_any_type():
    class AppSettings(Settings):
        HOST: str = Undefined

    assert AppSettings().is_valid()


#
# Validators
#


def test_settings_default_validators(is_positive):
    class TestSettings(Settings):
        default_validators = (is_positive,)

        MIN_SPEED = 0
        MAX_SPEED = 10

    test_settings = TestSettings()
    assert not test_settings.is_valid()
    assert 'MIN_SPEED' in test_settings.errors

    assert test_settings.errors['MIN_SPEED'] == ['Value should be positive']
    assert 'MAX_SPEED' not in test_settings.errors


def test_settings_mandatory_validators(is_positive, is_less_that_10):
    class TestSettings(Settings):
        mandatory_validators = (is_positive,)

        MIN_SPEED: int = Setting(0, validators=(is_less_that_10,))
        MAX_SPEED: int = Setting(11, validators=(is_less_that_10,))

    s = TestSettings()
    assert not s.is_valid()
    assert 'MIN_SPEED' in s.errors
    assert 'MAX_SPEED' in s.errors
    assert s.errors['MIN_SPEED'] == ['Value should be positive']
    assert s.errors['MAX_SPEED'] == ['Value should be less that 10']


#
# Nested settings
#


def test_settings_cannot_init_with_value():
    class TestSettings(Settings):
        ...

    with pytest.raises(AssertionError):
        TestSettings(value=10)


def test_settings_cannot_init_with_type_hint():
    class TestSettings(Settings):
        ...

    with pytest.raises(AssertionError):
        TestSettings(type_hint=int)


def test_nested_settings_valid():
    class NestedSettings(Settings):
        MAX_SPEED = 20

    class TestSettings(Settings):
        NESTED_SETTINGS = NestedSettings()

    assert TestSettings().is_valid()


def test_nested_setting_values():
    class HostSettings(Settings):
        NAME = 'localhost'

    class DBSettings(Settings):
        USERNAME = 'alex'
        HOST = HostSettings()

    class AppSettings(Settings):
        DB = DBSettings()

    app_settings = AppSettings()
    assert app_settings.is_valid()
    assert app_settings.DB.USERNAME == 'alex'
    assert app_settings.DB.HOST.NAME == 'localhost'


def test_nested_settings_validation_raises():
    class DBSettings(Settings):
        HOST: str = 10

    class AppSettings(Settings):
        DB = DBSettings()

    with pytest.raises(
        ValidationError,
        match=(
            "DB: HOST: Expected value of type `<class 'str'>` "
            "got value of type `<class 'int'>`"
        ),
    ):
        app_settings = AppSettings()
        app_settings.is_valid(raise_exception=True)


def test_nested_triple_nested_validation_errors():
    class HostSettings(Settings):
        NAME: str = 10

    class DBSettings(Settings):
        HOST = HostSettings()

    class AppSettings(Settings):
        DB = DBSettings()

    app_settings = AppSettings()
    assert not app_settings.is_valid()
    # fmt: off
    assert app_settings.errors == {'DB': [{'HOST': [{'NAME': [
        "Expected value of type `<class 'str'>` got value of type `<class 'int'>`"
    ]}]}]}
    # fmt: on


def test_validate_called():
    validate_called = False

    class TestSettings(Settings):
        def validate(self):
            nonlocal validate_called
            validate_called = True
            return {}

    assert TestSettings().is_valid()
    assert validate_called


def test_error_preserved_when_validate_raises_settings_validation_error():
    class TestSettings(Settings):
        def validate(self):
            raise ValidationError('there was an error XXXX')

    test_settings = TestSettings()
    assert not test_settings.is_valid()
    assert test_settings.errors == {INVALID_SETTINGS: ['there was an error XXXX']}


def test_error_raised_when_validate_raises_settings_validation_error():
    class TestSettings(Settings):
        def validate(self):
            raise ValidationError('there was an error XXXX')

    test_settings = TestSettings()
    with pytest.raises(ValidationError, match='there was an error XXXX'):
        test_settings.is_valid(raise_exception=True)


def test_settings_errors_readonly():
    class TestSettings(Settings):
        ...

    with pytest.raises(AttributeError):
        TestSettings().errors = {}


# prefix


def test_prefix_empty_field_not_allowed():
    with pytest.raises(ValueError, match='prefix cannot be empty'):
        @prefix('')
        class MySettings(Settings):
            ...


@pytest.mark.parametrize('invalid_prefix', ['1', '.', '-'])
def test_prefix_bad_identifier_not_allowed(invalid_prefix):
    with pytest.raises(ValueError, match='prefix should be a valid Python identifier'):
        @prefix(invalid_prefix)
        class MySettings(Settings):
            ...


def test_prefix_adds_underscore_suffix():
    @prefix('MY')
    class MySettings(Settings):
        SPEED = 10
        NAME = 'alex'

    assert hasattr(MySettings, 'MY_SPEED')
    assert hasattr(MySettings, 'MY_NAME')


def test_prefix_removes_prefixed_attribute_name():
    @prefix('MY')
    class MySettings(Settings):
        SPEED = 10

    assert not hasattr(MySettings, 'SPEED')


def test_prefix_sets_setting_name():
    @prefix('MY')
    class MySettings(Settings):
        SPEED = 10

    assert MySettings.MY_SPEED.name == 'MY_SPEED'


def test_prefix_cannot_decorate_not_settings_class():
    with pytest.raises(
        AssertionError, match='Intended to decorate Settings sub-classes only'
    ):
        @prefix('MY')
        class NotSettings:
            ...


def test_prefix_cannot_decorate_settings_with_existing_matching_field():
    with pytest.raises(
        ValueError,
        match='''MySettings'> class already has setting attribute named "GEAR"''',
    ):
        @prefix('MY')
        class MySettings(Settings):
            GEAR = 10
            MY_GEAR = 1


def test_settings_extract_to_module(build_module_mock):
    class MySettings(Settings):
        DEBUG = True
        SITE_NAME = 'mysite'

    module = build_module_mock('test_settings')
    MySettings().extract_to(module)
    assert module.DEBUG
    assert module.SITE_NAME == 'mysite'


def test_nested_settings_extract_to_dict():
    class DBSettings(Settings):
        USERNAME = 'alex'
        PASSWORD = 'secret_password'

    class MySettings(Settings):
        DB = DBSettings()

    d = {}
    MySettings().extract_to(d)
    assert d['DB_USERNAME'] == 'alex'
    assert d['DB_PASSWORD'] == 'secret_password'
