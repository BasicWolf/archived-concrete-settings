import random
import types

import factory
import pytest
from factory.fuzzy import FuzzyInteger, FuzzyFloat, FuzzyText

from concrete_settings import (Settings, Setting, SealedSetting, OverrideSetting,
                               exceptions)

seed = random.randint(1, 1e9)
print(f'Running tests with seed: {seed:0>10}')
factory.fuzzy.reseed_random(seed)


INT_VAL: int = FuzzyInteger(-10e10, 10e10).fuzz()
FLOAT_VAL: float = FuzzyFloat(-10e10, 10e10).fuzz()
STR_VAL: str = FuzzyText(length=FuzzyInteger(1, 255).fuzz()).fuzz()

STR_CONST: str = 'HELLO DESCRIPTION'





# ======================= Fixtures ================================= #
# ================================================================== #


@pytest.fixture
def make_dummy_validator():
    def _make_dummy_validator():
        return lambda settings, val: None
    return _make_dummy_validator


# ========================== Tests ================================= #
# ================================================================== #

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

        def DEMO(self) -> int:
            return self.x

    DEMO = S0.__dict__['DEMO']
    assert isinstance(DEMO, Setting)
    assert DEMO.type_hint is int
    assert S0().DEMO == INT_VAL


def test_method_not_converted_to_setting():
    class S0(Settings):
        x = INT_VAL

        def demo(self) -> int:
            return self.x

    assert isinstance(S0.demo, types.FunctionType)
    assert S0().demo() == INT_VAL


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
    assert DEMO.description == STR_CONST
    assert DEMO.validators == (dummy_validator, )
    assert DEMO.type_hint is int
    assert S1().DEMO == INT_VAL + 1


def test_description_change_in_derived_settings_error():
    class S0(Settings):
        DEMO: int = Setting(INT_VAL, STR_CONST)

    with pytest.raises(exceptions.DescriptionDiffersError) as e:
        class S1(S0):
            DEMO: int = Setting(INT_VAL, STR_CONST + 'a')
    e.match('has a different description')


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


def test_undefined_get_not_allowed():
    class S0(Settings):
        DEMO: int = Setting()

    with pytest.raises(exceptions.UndefinedValueError) as e:
         S0().DEMO
    assert(e.match('value has not been set'))


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


def test_invalid_multi_inheritance_order_fails():
    class A(Settings): pass
    class B(Settings): pass
    class C(A,B) : pass
    class D(B,A): pass

    with pytest.raises(TypeError) as e:
        class E(C,D): pass
    e.match('Cannot create a consistent method resolution')
