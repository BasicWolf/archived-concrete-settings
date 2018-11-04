import os
import sys
import types

import pytest

from concrete_settings import (
    Settings, Setting, SealedSetting, OverrideSetting, RequiredSetting,
    exceptions, SettingsHistory, settings_from_module, setting
)


from .common import INT_VAL, FLOAT_VAL, STR_VAL, STR_CONST


# ======================= Fixtures ================================= #
# ================================================================== #


@pytest.fixture
def make_dummy_validator():
    def _make_dummy_validator():
        return lambda settings, val: None
    return _make_dummy_validator

@pytest.fixture
def settings_module():
    name = 'my_settings'
    mod = types.ModuleType(name, 'my settings docstring')
    mod.__file__ =  name + '.py'
    sys.modules[name] = mod

    mod.DEMO = INT_VAL
    mod.STR_DEMO = STR_VAL
    return mod

# ========================== Tests ================================= #
# ================================================================== #

def test_setting_stored_per_class():
    class S0(Settings):
        DEMO: int = INT_VAL

    class S1(Settings):
        DEMO = INT_VAL + 1

    assert S0.DEMO != S1.DEMO


def test_value_stored_per_object():
    class S0(Settings):
        DEMO: int = INT_VAL

    s1 = S0()
    s2 = S0()

    s1.DEMO = INT_VAL + 1
    s2.DEMO = INT_VAL + 2

    assert S0.DEMO != s1.DEMO
    assert S0.DEMO != s2.DEMO


def test_value_attribute_converted_to_setting():
    class S0(Settings):
        DEMO: int = INT_VAL

    DEMO = S0.__dict__['DEMO']
    assert isinstance(DEMO, Setting)
    assert DEMO.type_hint is int
    assert S0.DEMO == INT_VAL
    assert S0().DEMO == INT_VAL


def test_value_attribute_not_converted_to_setting():
    class S0(Settings):
        demo: int = INT_VAL

    assert isinstance(S0.demo, int)
    assert S0().demo == INT_VAL


def test_method_converted_to_setting():
    class S0(Settings):
        x = INT_VAL

        @setting
        def DEMO(self) -> int:
            """This is demo doc"""
            return self.x

    DEMO = S0.__dict__['DEMO']
    assert isinstance(DEMO, Setting)
    assert DEMO.type_hint is int
    assert S0.DEMO.__annotations__['return'] == int
    assert S0.DEMO.__doc__ == 'This is demo doc'
    assert S0().DEMO == INT_VAL


def test_value_change_in_derived_settings():
    class S0(Settings):
        DEMO: int = INT_VAL + 1

    class S1(S0):
        DEMO = INT_VAL

    DEMO = S1.__dict__['DEMO']
    assert isinstance(DEMO, Setting)
    assert S1().DEMO == INT_VAL


def test_setting_attributes_copied_in_derived_settings(make_dummy_validator):
    dummy_validator = make_dummy_validator()

    class S0(Settings):
        DEMO: int = Setting(INT_VAL, STR_CONST, dummy_validator)

    class S1(S0):
        DEMO = INT_VAL + 1

    DEMO = S1.__dict__['DEMO']
    assert DEMO.__doc__ == STR_CONST
    assert DEMO.validators == (dummy_validator, )
    assert DEMO.type_hint is int
    assert S1().DEMO == INT_VAL + 1


def test_doc_change_in_derived_settings_error():
    class S0(Settings):
        DEMO: int = Setting(INT_VAL, STR_CONST)

    with pytest.raises(exceptions.DocDiffersError) as e:
        class S1(S0):
            DEMO: int = Setting(INT_VAL, STR_CONST + 'a')
    e.match('has a different docstring')


def test_sealed_setting_change_error():
    class S0(Settings):
        DEMO: int = SealedSetting(INT_VAL)

    with pytest.raises(exceptions.SealedSettingError) as e:
        class S1(S0):
            DEMO = INT_VAL + 1
    e.match('is sealed and cannot be changed')


def test_setting_change_type_in_derived_settings_error():
    class S0(Settings):
        DEMO: int = INT_VAL

    with pytest.raises(exceptions.TypeHintDiffersError) as e:
        class S1(S0):
            DEMO = Setting(FLOAT_VAL)
    e.match('has a different type hint')


def test_attribute_change_in_derived_settings_error():
    class S0(Settings):
        demo: int = INT_VAL

    with pytest.raises(exceptions.AttributeShadowError) as e:
        class S1(S0):
            demo = Setting(INT_VAL)
    e.match('overrides an existing attribute')


def test_validators_excluded_in_derived_settings_error(make_dummy_validator):
    dv_1 = make_dummy_validator()
    dv_2 = make_dummy_validator()
    dv_3 = make_dummy_validator()

    class S0(Settings):
        DEMO: int = Setting(INT_VAL, validators=(dv_1, dv_2))

    # this should run fine
    class S1(Settings):
        DEMO: int = Setting(INT_VAL, validators=(dv_1, dv_2, dv_3))

    with pytest.raises(exceptions.ValidatorsDiffersError) as e:
        class S2(S0):
            DEMO = Setting(INT_VAL, validators=(dv_1, dv_3))
    e.match('has different validators')


def test_non_settings_base_classes_not_allowed():
    class NS0: pass

    with pytest.raises(TypeError) as e:
        class S1(NS0, Settings):
            DEMO: int = INT_VAL
    assert e.match('inherit')


def test_required_setting():
    class S0(Settings):
        DEMO: int = RequiredSetting()

    with pytest.raises(exceptions.RequiredSettingIsUndefined) as e:
         S0()
    assert(e.match('required to have a value'))


def test_multi_inheritance_non_basic():
    class SA(Settings):
        AQUA: float = FLOAT_VAL

    class SB(Settings):
        VITA: int = INT_VAL

    class SAB(SB, SA): pass

    sab = SAB()
    assert sab.AQUA == FLOAT_VAL
    assert sab.VITA == INT_VAL


def test_multi_inheritance_override_error():
    class SA(Settings):
        DEMO: int = INT_VAL

    class SB(Settings):
        DEMO: str = STR_VAL

    with pytest.raises(exceptions.TypeHintDiffersError):
        class SAB(SB, SA): pass


def test_multi_inheritance_resolution_order():
    class SA(Settings):
        DEMO: int = INT_VAL

    class SB(Settings):
        DEMO: str = OverrideSetting(STR_VAL)

    class SAB(SB, SA): pass

    sab = SAB()
    assert sab.DEMO == STR_VAL


def test_invalid_multi_inheritance_order_error():
    class A(Settings): pass
    class B(Settings): pass
    class C(A,B) : pass
    class D(B,A): pass

    with pytest.raises(TypeError) as e:
        class E(C,D): pass
    e.match('Cannot create a consistent method resolution')


def test_settings_storage_attribute_defined_explicitly_error():
    with pytest.raises(AttributeError) as e:
        class S0(Settings):
            __settings_values__ = {}
    e.match('should not be defined explicitly')


def test_settings_from_module(settings_module):
    S0 = settings_from_module(settings_module)
    assert issubclass(S0, Settings)
    assert S0.DEMO == INT_VAL
    assert S0.STR_DEMO == STR_VAL
    assert S0.__dict__['DEMO'].type_hint is int
    assert S0.__dict__['STR_DEMO'].type_hint is str


def test_settings_from_module_filter(settings_module):
    S0 = settings_from_module(settings_module, name_filter=lambda s: s == 'DEMO')
    assert 'DEMO' in S0.__dict__
    assert 'STR_DEMO' not in S0.__dict__


def test_guess_type():
    class S0(Settings):
        # Numeric types
        S_BOOLEAN = True
        S_INT = 10
        S_FLOAT = 10.0
        S_COMPLEX = 10 + 10j

        # Sequences
        S_LIST = list()
        S_TUPLE = tuple()
        S_RANGE = range(3)

        # Text, Binary
        S_STR = 'str'
        S_BYTES = b'abc'

        # set, frozenset, dict
        S_SET = set()
        S_FROZENSET = frozenset()
        S_DICT = dict()

    d = S0.__dict__
    assert d['S_BOOLEAN'].type_hint is bool
    assert d['S_INT'].type_hint is int
    assert d['S_FLOAT'].type_hint is float
    assert d['S_COMPLEX'].type_hint is complex
    assert d['S_LIST'].type_hint is list
    assert d['S_TUPLE'].type_hint is tuple
    assert d['S_RANGE'].type_hint is range
    assert d['S_STR'].type_hint is str
    assert d['S_BYTES'].type_hint is bytes
    assert d['S_SET'].type_hint is set
    assert d['S_FROZENSET'].type_hint is frozenset
    assert d['S_DICT'].type_hint is dict


def test_method_not_converted_to_setting():
    class S0(Settings):
        x = INT_VAL

        def demo(self) -> int:
            return self.x

    assert isinstance(S0.demo, types.FunctionType)
    assert S0().demo() == INT_VAL


def test_callable_types_are_not_settings():
    class S0(Settings):
        S_INT = INT_VAL

        @property
        def PROP_BOOLEAN(self):
            return False

        def FUNC(self):
            return STR_VAL

        @classmethod
        def CLASS_METH(cls):
            return cls

        @staticmethod
        def STATIC_METH():
            return STR_VAL

    assert S0.S_INT == INT_VAL
    assert isinstance(S0.PROP_BOOLEAN, property)
    assert isinstance(S0.FUNC, types.FunctionType)
    assert isinstance(S0.CLASS_METH, types.MethodType)
    assert isinstance(S0.STATIC_METH, types.FunctionType)

    s0 = S0()
    assert s0.PROP_BOOLEAN == False
    assert s0.FUNC() == STR_VAL
    assert s0.CLASS_METH() == S0
    assert s0.STATIC_METH() == STR_VAL


def test_settings_from_env_variables(monkeypatch):
    with monkeypatch.context() as m:
        m.setitem(os.environ, 'S_STR', STR_VAL)

        class S0(Settings):
            S_STR = Setting(env='S_STR')
            S_STR2 = Setting(env=True)

        assert S0.S_INT == INT_VAL
