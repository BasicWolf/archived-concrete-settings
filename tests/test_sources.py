import pytest
from concrete_settings import Settings
from concrete_settings.sources import get_source, DictSource, NoSuitableSourceFoundError


def test_get_source_fail_for_unknown_source():
    with pytest.raises(NoSuitableSourceFoundError):
        assert get_source('/test/dummy')


#
# Update Dict
#


def test_get_dict_source():
    dsrc = get_source({'a': 10})
    assert isinstance(dsrc, DictSource)
    assert dsrc.read() == {'a': 10}


def test_update_empty_dict():
    class S(Settings):
        pass

    S().update({})


def test_update_with_extra_data_has_no_effect_on_settings():
    class S(Settings):
        pass

    s = S()
    s.update({'X': 10})
    assert not hasattr(s, 'X')


def test_update_top_level_setting():
    class S(Settings):
        T: int = 10

    s = S()
    s.update({'T': 100})
    assert s.T == 100


def test_update_nested_setting():
    class S(Settings):
        T: int = 10

    class S1(Settings):
        NESTED_S = S()

    s1 = S1()
    # fmt: off
    s1.update({
        'NESTED_S': {
            'T': 20
        }
    })
    # fmt: on
    assert s1.NESTED_S.T == 20


def test_env_source(monkeypatch):
    monkeypatch
