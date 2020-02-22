import importlib
import sys
import typing
from collections import namedtuple

import pytest

import concrete_settings
from concrete_settings import INVALID_SETTINGS, Settings, Setting, Undefined, prefix
from concrete_settings.exceptions import SettingsValidationError


def test_cls_init_empty_settings():
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
    class S0(Settings):
        DEMO: int = v_int
        demo: str = v_int

    assert isinstance(S0.DEMO, Setting)
    assert S0.__dict__["DEMO"].type_hint is int
    assert isinstance(S0.demo, int)


def test_setting_set(v_int):
    class S0(Settings):
        DEMO: int = v_int

    class S1(Settings):
        DEMO = v_int + 1

    assert S0().DEMO != S1().DEMO


def test_guessed_type():
    class S(Settings):
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

    d = S.__dict__
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
    class S(Settings):
        ...

    s = S()
    s.is_valid()


def test_setting_is_validated():
    validate_called = False

    def validator(value, **_):
        nonlocal validate_called
        validate_called = True

    class S(Settings):
        T = Setting(10, validators=(validator,))

    assert S().is_valid()
    assert validate_called


#
# ValueTypeValidator
#


def test_value_type_validator():
    class S(Settings):
        T: str = 10

    with pytest.raises(
        SettingsValidationError,
        match="Expected value of type `<class 'str'>` got value of type `<class 'int'>`",
    ):
        S().is_valid(raise_exception=True)


def test_value_type_validator_with_inheritance():
    class S0(Settings):
        T: str = 10

    class S1(S0):
        T = 'abc'

    assert S1().is_valid()


def test_value_type_validator_allows_undefined_for_any_type():
    class AppSettings(Settings):
        HOST: str = Undefined

    assert AppSettings().is_valid()


#
# Validators
#


def test_settings_default_validators(is_positive):
    class S(Settings):
        default_validators = (is_positive,)

        T0 = 0
        T1 = 10

    s = S()
    assert not s.is_valid()
    assert 'T0' in s.errors

    assert s.errors['T0'] == [f'Value should be positive']
    assert 'T1' not in s.errors


def test_settings_mandatory_validators(is_positive, is_less_that_10):
    class S(Settings):
        mandatory_validators = (is_positive,)

        T0: int = Setting(0, validators=(is_less_that_10,))
        T1: int = Setting(11, validators=(is_less_that_10,))

    s = S()
    assert not s.is_valid()
    assert 'T0' in s.errors
    assert 'T1' in s.errors
    assert s.errors['T0'] == ['Value should be positive']
    assert s.errors['T1'] == ['Value should be less that 10']


#
# Nested settings
#


def test_settings_cannot_init_with_value():
    class S(Settings):
        ...

    with pytest.raises(AssertionError):
        S(value=10)


def test_settings_cannot_init_with_type_hint():
    class S(Settings):
        ...

    with pytest.raises(AssertionError):
        S(type_hint=int)


def test_nested_settings_valid():
    class S2(Settings):
        VAL2 = 20

    class S1(Settings):
        NESTED_S2 = S2()

    s1 = S1()
    assert s1.is_valid()


def test_nested_setting_values():
    class S3(Settings):
        VAL3 = 30

    class S2(Settings):
        VAL2 = 20
        NESTED_S3 = S3()

    class S1(Settings):
        NESTED_S2 = S2()

    s1 = S1()
    assert s1.is_valid()
    assert s1.NESTED_S2.VAL2 == 20
    assert s1.NESTED_S2.NESTED_S3.VAL3 == 30


def test_nested_settings_validation_raises():
    class S0(Settings):
        T: str = 10

    class S(Settings):
        T_S0 = S0()

    with pytest.raises(
        SettingsValidationError,
        match=(
            "T_S0: Expected value of type `<class 'str'>` "
            "got value of type `<class 'int'>`"
        ),
    ):
        s = S()
        s.is_valid(raise_exception=True)


def test_nested_triple_nested_validation_errors():
    class S3(Settings):
        Т: str = 10

    class S2(Settings):
        NESTED_S3 = S3()

    class S1(Settings):
        NESTED_S2 = S2()

    s1 = S1()
    assert not s1.is_valid()
    # fmt: off
    assert s1.errors == {'NESTED_S2': [{'NESTED_S3': [{'Т': [
        "Expected value of type `<class 'str'>` got value of type `<class 'int'>`"
    ]}]}]}
    # fmt: on


def test_validate_called():
    validate_called = False

    class S(Settings):
        def validate(self):
            nonlocal validate_called
            validate_called = True
            return {}

    assert S().is_valid()
    assert validate_called


def test_error_preserved_when_validate_raises_settings_validation_error():
    class S(Settings):
        def validate(self):
            raise SettingsValidationError('there was an error XXXX')

    s = S()
    assert not s.is_valid()
    assert s.errors == {INVALID_SETTINGS: ['there was an error XXXX']}


def test_error_raised_when_validate_raises_settings_validation_error():
    class S(Settings):
        def validate(self):
            raise SettingsValidationError('there was an error XXXX')

    s = S()
    with pytest.raises(SettingsValidationError, match='there was an error XXXX'):
        s.is_valid(raise_exception=True)


def test_settings_errors_readonly():
    class S(Settings):
        T: int = 10

    with pytest.raises(AttributeError):
        S().errors = {}


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
