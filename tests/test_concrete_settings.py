import importlib
import types
import typing
import sys
from collections import namedtuple

import pytest

import concrete_settings
from concrete_settings import Settings, Setting, setting
from concrete_settings.sources import Source
from concrete_settings.behaviors import override
from concrete_settings.exceptions import SettingsValidationError
from .utils import Match


@pytest.fixture
def unsupported_python_version_info():
    VersionInfo = namedtuple(
        'version_info', ['major', 'minor', 'micro', 'releaselevel', 'serial']
    )
    return VersionInfo(3, 5, 0, 'final', 0)


def test_smoke():
    assert True


def test_cls_init_empty_settings():
    Settings()


def test_import_in_unsupported_python_fails(mocker, unsupported_python_version_info):
    mocker.patch.object(sys, 'version_info', unsupported_python_version_info)
    with pytest.raises(
        ImportError, match="Python 3.6 or higher is required by concrete_settings"
    ):
        importlib.reload(concrete_settings)


def test_setting_ctor(v_int):
    validators = (lambda x: x,)
    s = Setting(
        v_int, type_hint=int, validators=validators, doc="docstring", behaviors=[]
    )

    assert s.value == v_int
    assert s.__doc__ == "docstring"
    assert s.validators is validators
    assert s.type_hint is int
    assert s.behaviors == []


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


def test_guess_type():
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


class TestPropertySetting:
    def test_with_setting_attrs_decorated_method(self, v_int):
        class S(Settings):
            @setting
            def T(self) -> int:
                """T docs"""
                return v_int

        assert S.T.__doc__ == "T docs"
        assert S.T.validators == tuple()
        assert S.T.type_hint == int
        s = S()
        assert s.T == v_int

    def test_no_return_type_hint(self, v_int):
        class S(Settings):
            @setting
            def T(self):
                return v_int

        assert S.T.type_hint is typing.Any

    def test_with_setting_attrs_defined_as_argument(self, DummyValidator, v_int):
        class S(Settings):
            @setting(type_hint=int, doc="T arg docs", validators=(DummyValidator(),))
            def T(self):
                return v_int

        assert S.T.__doc__ == "T arg docs"
        assert S.T.type_hint == int
        assert len(S.T.validators) == 1
        assert isinstance(S.T.validators[0], DummyValidator)

    def test_property_setting_using_other_settings(self):
        class S(Settings):
            A: int = 10
            B: str = 'hello world'

            @setting
            def AB(self) -> str:
                return f'{self.A} {self.B}'

        s = S()
        assert s.AB == '10 hello world'


def test_callable_types_are_not_settings(v_int, v_str):
    class S(Settings):
        INT = v_int

        @property
        def PROP_BOOLEAN(self):
            return False

        def FUNC(self):
            return v_str

        @classmethod
        def CLASS_METH(cls):
            return cls

        @staticmethod
        def STATIC_METH():
            return v_str

    assert S.INT.value == v_int
    assert isinstance(S.PROP_BOOLEAN, property)
    assert isinstance(S.FUNC, types.FunctionType)
    assert isinstance(S.CLASS_METH, types.MethodType)
    assert isinstance(S.STATIC_METH, types.FunctionType)

    s = S()
    assert not s.PROP_BOOLEAN
    assert s.FUNC() == v_str
    assert s.CLASS_METH() == S
    assert s.STATIC_METH() == v_str


def test_validate_smoke():
    class S(Settings):
        pass

    s = S()
    s.is_valid()


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


def test_nested_settings_smoke():
    class S0(Settings):
        T = 10

    class S(Settings):
        NESTED_S0 = S0()

    s = S()
    s.is_valid()


def test_nested_setting_values():
    class S3(Settings):
        VAL3 = 30

    class S2(Settings):
        VAL2 = 20
        NESTED_S3 = S3()

    class S1(Settings):
        NESTED_S2 = S2()

    s1 = S1()
    assert s1.NESTED_S2.VAL2 == 20
    assert s1.NESTED_S2.NESTED_S3.VAL3 == 30


def test_nested_settings_validation_raises():
    class S0(Settings):
        T: str = 10

    class S(Settings):
        T_S0 = S0()

    with pytest.raises(
        SettingsValidationError,
        match="T_S0: Expected value of type `<class 'str'>` got value of type `<class 'int'>`",
    ) as e:
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


#
# Updating
#


def test_update_source_is_not_called_on_empty(mocker):
    class S(Settings):
        pass

    s = S()
    src_mock = mocker.Mock(spec=Source)

    s.update(src_mock)
    src_mock.read.assert_not_called()


def test_update_top_level_setting_source_is_called(mocker):
    class S(Settings):
        T: int = 10

    s = S()
    src_mock = mocker.Mock(spec=Source)
    src_mock = mocker.Mock(spec=Source)
    src_mock.read = mocker.MagicMock(return_value=10)

    s.update(src_mock)
    src_mock.read.assert_called_with(Match(lambda arg: arg.name == 'T'), ())


def test_update_top_level_setting_from_source(mocker):
    class S(Settings):
        T: int = 10

    s = S()
    src_mock = mocker.Mock(spec=Source)
    src_mock = mocker.Mock(spec=Source)
    src_mock.read = mocker.MagicMock(side_effect=lambda *ignore: 10)

    s.update(src_mock)
    assert s.T == 10


def test_update_nested_setting_source_is_called(mocker):
    class S(Settings):
        T: int = 10

    class S1(Settings):
        NESTED_S = S()

    s1 = S1()
    src_mock = mocker.Mock(spec=Source)
    src_mock.read = mocker.MagicMock()

    s1.update(src_mock)

    src_mock.read.assert_called_once_with(
        Match(lambda arg: arg.name == 'T'), ('NESTED_S',)
    )


def test_update_nested_setting_from_source(mocker):
    class S(Settings):
        T: int = 10

    class S1(Settings):
        NESTED_S = S()

    s1 = S1()
    src_mock = mocker.Mock(spec=Source)
    src_mock.read = mocker.MagicMock(return_value=20)

    s1.update(src_mock)
    assert s1.NESTED_S.T == 20
