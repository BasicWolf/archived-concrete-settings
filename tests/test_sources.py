from typing import Dict

import pytest
from concrete_settings import Setting
from concrete_settings.sources import (
    DictSource,
    EnvVarSource,
    JsonSource,
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


def test_string_source_mixin_convert_int_value():
    assert StringSourceMixin.convert_value('10', int) == 10


def test_string_source_mixin_convert_float_value():
    assert StringSourceMixin.convert_value('10.25', float) == 10.25


@pytest.mark.parametrize('true_str', ('true', 'True', 'TRUE'))
def test_string_source_mixin_convert_true_value(true_str):
    assert StringSourceMixin.convert_value(true_str, bool) == True


@pytest.mark.parametrize('false_str', ('false', 'False', 'FALSE'))
def test_string_source_mixin_convert_false_value(false_str):
    assert StringSourceMixin.convert_value(false_str, bool) == False


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


#
# ENV source
#


def test_get_env_source_returns_env_source():
    esrc = get_source(EnvVarSource())
    assert isinstance(esrc, EnvVarSource)


def test_env_source_one_level_values(monkeypatch):
    monkeypatch.setenv('a', '10')
    esrc = get_source(EnvVarSource())
    assert esrc.read(S('a')) == '10'


def test_env_source_int_hint(monkeypatch):
    monkeypatch.setenv('a', '10')
    esrc = get_source(EnvVarSource())
    assert esrc.read(S('a', int)) == 10


def test_env_source_int_hint(monkeypatch):
    monkeypatch.setenv('a', '10.25')
    esrc = get_source(EnvVarSource())
    assert esrc.read(S('a', float)) == 10.25


#
# JSON filesource
#


def test_get_json_file_returns_json_source():
    src = get_source('/test/settings.json')
    assert isinstance(src, JsonSource)


def test_json_source_has_expected_path(fs):
    fs.create_file('/test/settings.json', contents='')
    jsrc = get_source('/test/settings.json')
    assert jsrc.path == '/test/settings.json'


def test_json_source_read_int_value(fs):
    fs.create_file('/test/settings.json', contents='{"A": 10}')
    jsrc = get_source('/test/settings.json')
    assert jsrc.read(S('A')) == 10


def test_json_source_read_float_value(fs):
    fs.create_file('/test/settings.json', contents='{"A": 10.25}')
    jsrc = get_source('/test/settings.json')
    assert jsrc.read(S('A')) == 10.25


def test_json_source_read_str_value(fs):
    fs.create_file('/test/settings.json', contents='{"A": "abc"}')
    jsrc = get_source('/test/settings.json')
    assert jsrc.read(S('A')) == "abc"


def test_json_source_read_null_value(fs):
    fs.create_file('/test/settings.json', contents='{"A": null}')
    jsrc = get_source('/test/settings.json')
    assert jsrc.read(S('A')) is None


def test_json_source_read_array_value(fs):
    fs.create_file('/test/settings.json', contents='{"A": [1, 2, 3]}')
    jsrc = get_source('/test/settings.json')
    assert jsrc.read(S('A')) == [1, 2, 3]


def test_json_source_read_object_value(fs):
    fs.create_file('/test/settings.json', contents='{"A": {"B": 10}}')
    jsrc = get_source('/test/settings.json')
    assert jsrc.read(S('A')) == {"B": 10}


def test_json_source_read_nested_object_value(fs):
    fs.create_file('/test/settings.json', contents='{"A": {"B": 10}}')
    jsrc = get_source('/test/settings.json')
    assert jsrc.read(S('B'), parents=('A',)) == 10


#
# YAML source
#


def test_get_yaml_file_returns_yaml_source():
    src = get_source('/test/settings.yaml')
    assert isinstance(src, JsonSource)

    src = get_source('/test/settings.yml')
    assert isinstance(src, JsonSource)


# def test_json_source_has_expected_path(fs):
#     fs.create_file('/test/settings.json', contents='')
#     jsrc = get_source('/test/settings.json')
#     assert jsrc.path == '/test/settings.json'


# def test_json_source_read_int_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": 10}')
#     jsrc = get_source('/test/settings.json')
#     jsrc.read(S('A')) == 10


# def test_json_source_read_float_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": 10.25}')
#     jsrc = get_source('/test/settings.json')
#     jsrc.read(S('A')) == 10.25


# def test_json_source_read_str_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": "abc"}')
#     jsrc = get_source('/test/settings.json')
#     jsrc.read(S('A')) == "abc"


# def test_json_source_read_null_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": null}')
#     jsrc = get_source('/test/settings.json')
#     jsrc.read(S('A')) == None


# def test_json_source_read_array_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": [1, 2, 3]}')
#     jsrc = get_source('/test/settings.json')
#     jsrc.read(S('A')) == [1, 2, 3]


# def test_json_source_read_object_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": {"B": 10}}')
#     jsrc = get_source('/test/settings.json')
#     jsrc.read(S('A')) == {"B": 10}


# def test_json_source_read_nested_object_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": {"B": 10}}')
#     jsrc = get_source('/test/settings.json')
#     jsrc.read(S('B'), parents=('A',)) == 10
