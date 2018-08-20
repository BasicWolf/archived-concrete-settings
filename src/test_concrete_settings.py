import pytest

from concrete_settings import Setting, Settings


@pytest.fixture
def c_empty():
    class C(Settings):
        demo = Setting()
    return C()


@pytest.fixture
def c_sealed():
    class C(Settings):
        demo = Setting(10, sealed=True)
    return C()


@pytest.fixture
def c_int_cls():
    class C(Settings):
        demo: int = Setting(34, 'An integer setting')
    return C

@pytest.fixture
def c_int():
    class C(Settings):
        demo: int = Setting(34, 'An integer setting')
    return C()


def test_empty_setting(c_empty):
    with pytest.raises(ValueError) as e:
        c_empty.demo
    assert e.match('C_demo')


def test_sealed(c_sealed):
    with pytest.raises(AttributeError) as e:
        c_sealed.demo = 30
    assert e.match('sealed')


def test_simple_inheritance(c_int_cls):
    class D(c_int_cls):
        demo_d = 40

    class Mixin:
        x = 30

    import pudb.b
    class E(D, Mixin):
        demo_e = 50


def test_get_value(c_int):
    assert c_int.demo == 34
