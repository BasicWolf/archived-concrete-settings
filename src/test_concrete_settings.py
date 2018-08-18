import pytest

from concrete_settings import Setting


@pytest.fixture
def c_empty():
    class C:
        demo = Setting()
    return C()


@pytest.fixture
def c_sealed():
    class C:
        demo = Setting(10, sealed=True)
    return C()


@pytest.fixture
def c_int():
    class C:
        demo = Setting(34, int, 'An integer setting')
    return C()


def test_empty_setting(c_empty):
    with pytest.raises(ValueError) as e:
        c_empty.demo
    assert e.match('C_demo')


def test_sealed(c_sealed):
    with pytest.raises(AttributeError) as e:
        c_sealed.demo = 30
    assert e.match('sealed')

def test_get_value(c_int):
    assert c_int.demo == 34
