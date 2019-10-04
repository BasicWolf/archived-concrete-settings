import sys

import pytest

from concrete_settings import Setting
from concrete_settings.contrib.sources import EnvVarSource, JsonSource, YamlSource
from concrete_settings.exceptions import ConcreteSettingsError
from concrete_settings.sources import get_source


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


def test_env_source_float_hint(monkeypatch):
    monkeypatch.setenv('a', '10.25')
    esrc = get_source(EnvVarSource())
    assert esrc.read(S('a', float)) == 10.25


def test_env_source_with_parents(monkeypatch):
    monkeypatch.setenv('DB_USER', 'alex')
    esrc = get_source(EnvVarSource())
    assert esrc.read(S('USER', str), ('DB',)) == 'alex'
    assert esrc.read(S('USER', str), ('db',)) == 'alex'


#
# JSON filesource
#


def test_get_json_file_returns_json_source():
    src = get_source('/test/settings.json')
    assert isinstance(src, JsonSource)


def test_json_source_has_expected_path(fs):
    fs.create_file('/test/settings.json', contents='{}')
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


def S(name: str, type_hint=str) -> Setting:
    """A helper function which creates a setting and assigns it a name."""
    s = Setting(type_hint=type_hint)
    s.__set_name__(s, name)
    return s


def test_yaml_source_throws_import_error_when_module_missing(mocker):
    # buggy mocker.patch.dict, using manual context resoration
    _yaml = sys.modules.get('yaml', None)
    sys.modules['yaml'] = None

    with pytest.raises(ConcreteSettingsError) as excinfo:
        get_source('/test/settings.yaml')
    assert isinstance(excinfo.value.__cause__, ImportError)

    if _yaml is not None:
        sys.modules['yaml'] = _yaml
    else:
        del sys.modules['yaml']


def test_get_yaml_file_returns_yaml_source():
    src = get_source('/test/settings.yaml')
    assert isinstance(src, YamlSource)


def test_yaml_source_has_expected_path(fs):
    fs.create_file('/test/settings.yaml', contents='')
    ysrc = get_source('/test/settings.yaml')
    assert ysrc.path == '/test/settings.yaml'


def test_yaml_source_read_int_value(fs):
    fs.create_file('/test/settings.yaml', contents='A: 10')
    ysrc = get_source('/test/settings.yaml')
    assert ysrc.read(S('A')) == 10


def test_yaml_source_read_float_value(fs):
    fs.create_file('/test/settings.yaml', contents='A: 10.25')
    ysrc = get_source('/test/settings.yaml')
    assert ysrc.read(S('A')) == 10.25


def test_yaml_source_read_str_value(fs):
    fs.create_file('/test/settings.yaml', contents='A: abc')
    ysrc = get_source('/test/settings.yaml')
    assert ysrc.read(S('A')) == "abc"


def test_yaml_source_read_null_value(fs):
    fs.create_file('/test/settings.yaml', contents='A: null')
    ysrc = get_source('/test/settings.yaml')
    assert ysrc.read(S('A')) is None


def test_yaml_source_read_array_value(fs):
    fs.create_file(
        '/test/settings.yaml',
        contents='''
    A:
      - 1
      - 2
      - 3
    ''',
    )
    ysrc = get_source('/test/settings.yaml')
    assert ysrc.read(S('A')) == [1, 2, 3]


def test_yaml_source_read_object_value(fs):
    fs.create_file(
        '/test/settings.yaml',
        contents='''
    A:
      B: 10
    ''',
    )
    ysrc = get_source('/test/settings.yaml')
    assert ysrc.read(S('A')) == {'B': 10}


def test_yaml_source_read_nested_object_value(fs):
    fs.create_file(
        '/test/settings.yaml',
        contents='''
    A:
      B: 10
    ''',
    )
    ysrc = get_source('/test/settings.yaml')
    assert ysrc.read(S('B'), parents=('A',)) == 10
