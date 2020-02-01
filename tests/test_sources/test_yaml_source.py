import pytest

from concrete_settings import Setting
from concrete_settings.contrib.sources import YamlSource
from concrete_settings.exceptions import ConcreteSettingsError
from concrete_settings.sources import get_source


def S(name: str, type_hint=str) -> Setting:
    """A helper function which creates a setting and assigns it a name."""
    s = Setting(type_hint=type_hint)
    s.__set_name__(s, name)
    return s


def test_yaml_source_throws_import_error_when_module_missing(mocker):
    import sys

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


def test_yaml_source_read_non_existing_setting_returns_setting_value(fs):
    fs.create_file('/test/settings.yaml', contents='')
    ysrc = get_source('/test/settings.yaml')

    setting = S('NOT_EXISTS')
    setting.value = 'some default value'
    assert ysrc.read(setting) == 'some default value'
