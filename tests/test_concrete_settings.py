import types
from concrete_settings import (
    ConcreteSettings,
    Setting,
    OverrideSetting,
    SealedSetting,
)


def test_smoke():
    assert True


def test_cls_init_empty_settings():
    ConcreteSettings()


def test_setting_ctor(rint):
    validators = (lambda x: x,)
    s = Setting(rint, "docstring", validators, int)

    assert s.value == rint
    assert s.__doc__ == "docstring"
    assert s.validators is validators
    assert s.type_hint is int


def test_settings_converted_from_attributes(rint):
    class S0(ConcreteSettings):
        DEMO: int = rint
        demo: str = rint

    assert isinstance(S0.DEMO, Setting)
    assert S0.__dict__["DEMO"].type_hint is int
    assert isinstance(S0.demo, int)


def test_setting_set(rint):
    class S0(ConcreteSettings):
        DEMO: int = rint

    class S1(ConcreteSettings):
        DEMO = rint + 1

    assert S0().DEMO != S1().DEMO


def test_guess_type():
    class S(ConcreteSettings):
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
    class S(ConcreteSettings):
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
    class S(ConcreteSettings):
        pass

    s = S()


def test_validate_override_smoke(rint, rstr):
    class S(ConcreteSettings):
        T: int = rint

    class S1(S):
        T: str = OverrideSetting(rstr)

    assert S1().T == rstr
