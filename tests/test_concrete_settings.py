import types

import pytest

from concrete_settings import Settings, Setting, OverrideSetting, DeprecatedSetting

from concrete_settings import exceptions


def test_smoke():
    assert True


def test_cls_init_empty_settings():
    Settings()


def test_setting_ctor(rint):
    validators = (lambda x: x,)
    s = Setting(rint, "docstring", validators, int)

    assert s.value == rint
    assert s.__doc__ == "docstring"
    assert s.validators is validators
    assert s.type_hint is int


def test_settings_converted_from_attributes(rint):
    class S0(Settings):
        DEMO: int = rint
        demo: str = rint

    assert isinstance(S0.DEMO, Setting)
    assert S0.__dict__["DEMO"].type_hint is int
    assert isinstance(S0.demo, int)


def test_setting_set(rint):
    class S0(Settings):
        DEMO: int = rint

    class S1(Settings):
        DEMO = rint + 1

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


def test_callable_types_are_not_settings(rint, rstr):
    class S(Settings):
        INT = rint

        @property
        def PROP_BOOLEAN(self):
            return False

        def FUNC(self):
            return rstr

        @classmethod
        def CLASS_METH(cls):
            return cls

        @staticmethod
        def STATIC_METH():
            return rstr

    assert S.INT.value == rint
    assert isinstance(S.PROP_BOOLEAN, property)
    assert isinstance(S.FUNC, types.FunctionType)
    assert isinstance(S.CLASS_METH, types.MethodType)
    assert isinstance(S.STATIC_METH, types.FunctionType)

    s = S()
    assert s.PROP_BOOLEAN == False
    assert s.FUNC() == rstr
    assert s.CLASS_METH() == S
    assert s.STATIC_METH() == rstr


def test_validate_smoke():
    class S(Settings):
        pass

    s = S()
    s.is_valid()


def test_validate_override_smoke(rint, rstr):
    class S(Settings):
        T: int = rint

    class S1(S):
        T: str = OverrideSetting(rstr)

    s1 = S1()
    s1.is_valid()
    assert s1.T == rstr


def test_fail_validate_type_without_override(rint, rstr):
    class S(Settings):
        T: int = rint

    class S1(S):
        T: str = rstr

    s = S1()
    with pytest.raises(exceptions.SettingsValidationError) as e:
        s.is_valid(raise_exception=True)

        e.match('types differ')

    assert 'T' in s.errors


def test_deprecated_setting_raises_warning_when_validated():
    with pytest.warns(
        DeprecationWarning,
        match=r"Setting `D` in class `<class 'test_concrete_settings.test_deprecated_setting_raises_warning_when_validated.<locals>.S'>` is deprecated.",
    ) as w:

        class S(Settings):
            D = DeprecatedSetting(100)

        S().is_valid()
        assert len(w) == 1


def test_deprecated_setting_raises_warning_when_accessed():
    class S(Settings):
        D = DeprecatedSetting(100)

    with pytest.warns(DeprecationWarning):
        S().is_valid()

    with pytest.warns(
        DeprecationWarning,
        match=r"Setting `D` in class `<class 'test_concrete_settings.test_deprecated_setting_raises_warning_when_accessed.<locals>.S'>` is deprecated",
    ) as w:
        x = S().D
        assert len(w) == 1
