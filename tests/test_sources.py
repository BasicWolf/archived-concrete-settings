from typing import Dict

import pytest
from concrete_settings import Setting
from concrete_settings.sources import (
    EnvVarSource,
    DictSource,
    NoSuitableSourceFoundError,
    Source,
    StringSourceMixin,
    get_source,
)


def test_get_source_fail_for_unknown_source():
    with pytest.raises(NoSuitableSourceFoundError):
        assert get_source('/test/dummy')


#
# StringSourceMixin
#


def test_convert_int_value():
    pass


#
# Dict source
#


def S(name: str, type_hint=str) -> Setting:
    s = Setting(type_hint=type_hint)
    s.__set_name__(s, name)
    return s


def test_get_source_for_dict_retuns_dict_source():
    dsrc = get_source({'a': 10})
    assert isinstance(dsrc, DictSource)


def test_dict_source_one_level_values():
    dsrc = get_source({'a': 10, 'b': 20})
    assert dsrc.read(S('a')) == 10
    assert dsrc.read(S('b')) == 20


def test_dict_source_two_levels_nested_dicts_values():
    dsrc = get_source({'a': 10, 'c': {'d': 30}})
    assert dsrc.read(S('a')) == 10
    assert dsrc.read(S('c')) == {'d': 30}
    assert dsrc.read(S('d'), parents=('c',)) == 30


def test_get_env_source_returns_env_source():
    dsrc = get_source(EnvVarSource())
    assert isinstance(dsrc, EnvVarSource)


def test_env_source_one_level_values(monkeypatch):
    monkeypatch.setenv('a', '10')
    dsrc = get_source(EnvVarSource())
    assert dsrc.read(S('a')) == '10'


def test_env_source_int_hint(monkeypatch):
    monkeypatch.setenv('a', '10')
    dsrc = get_source(EnvVarSource())
    assert dsrc.read(S('a', int)) == 10
