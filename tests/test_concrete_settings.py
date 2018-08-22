import random
import types

import factory
import pytest
from factory.fuzzy import FuzzyInteger, FuzzyFloat, FuzzyText

from concrete_settings import Settings, Setting, SealedSetting, OverrideSetting

seed = random.randint(1, 1e9)
print(f'Running tests with seed: {seed:0>10}')
factory.fuzzy.reseed_random(seed)


INT_VAL: int = FuzzyInteger(-10e10, 10e10).fuzz()
FLOAT_VAL: float = FuzzyFloat(-10e10, 10e10).fuzz()
STR_VAL: str = FuzzyText(length=FuzzyInteger(1, 255).fuzz()).fuzz()

STR_CONST: str = 'HELLO DESCRIPTION'


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


def test_setting_attributes_copied_in_derived_settings():
    def dummy_validator(setting, val):
        pass

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

    with pytest.raises(AttributeError) as e:
        class S1(S0):
            DEMO: int = Setting(INT_VAL, STR_CONST + 'a')
    e.match('has a different description')


def test_sealed_setting_change_error():
    class S0(Settings):
        DEMO: int = SealedSetting(INT_VAL)

    with pytest.raises(AttributeError) as e:
        class S1(S0):
            DEMO = INT_VAL + 1
    e.match('is sealed and cannot be changed')


def test_setting_change_type_in_derived_settings_error():
    class S0(Settings):
        DEMO: int = INT_VAL

    with pytest.raises(AttributeError) as e:
        class S1(S0):
            DEMO = Setting(FLOAT_VAL)
    e.match('has a different type hint')


def test_attribute_change_in_derived_settings_error():
    class S0(Settings):
        demo: int = INT_VAL

    with pytest.raises(AttributeError) as e:
        class S1(S0):
            demo = Setting(INT_VAL)
    e.match('overrides an existing attribute')


def test_non_settings_base_classes_not_allowed():
    class NS0:
        pass

    with pytest.raises(TypeError) as e:
        class S1(NS0, Settings):
            DEMO: int = INT_VAL
    assert e.match('inherit')

# def test_empty_setting(c_empty):
#     with pytest.raises(ValueError) as e:
#         c_empty.demo
#     assert e.match('C_demo')


# def test_sealed(c_sealed):
#     with pytest.raises(AttributeError) as e:
#         c_sealed.demo = 30
#     assert e.match('sealed')


# def test_mixin_override(c_int_cls):
#     pass
#     class Mixin:
#         demo: float = Setting(FLOAT_VAL)

#     with pytest.raises(AttributeError) as e:
#         class X(Mixin, c_int_cls):
#             demo_str = Setting(STR_VAL)
#     assert e.match('Use OverrideSetting')


# def test_deep_mixin_override(c_int_cls):
#     class MixinMiddle:
#         demo = 30

#     class MixinTop:
#         demo: int = Setting(INT_VAL)

#     with pytest.raises(AttributeError) as e:
#         class X(MixinTop, MixinMiddle, c_int_cls):
#             pass

# def test_get_value(c_int):
#     assert c_int.demo == INT_VAL
