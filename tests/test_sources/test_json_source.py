from concrete_settings import Setting
from concrete_settings.contrib.sources import JsonSource
from concrete_settings.sources import get_source, NotFound


def S(name: str, type_hint=str) -> Setting:
    """A helper function which creates a setting and assigns it a name."""
    s = Setting(type_hint=type_hint)
    s.__set_name__(s, name)
    return s


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


def test_json_source_read_non_existing_setting_returns_not_found(fs):
    fs.create_file('/test/settings.json', contents='{"A": {"B": 10}}')
    jsrc = get_source('/test/settings.json')

    setting = S('NOT_EXISTS')
    assert jsrc.read(setting) == NotFound
