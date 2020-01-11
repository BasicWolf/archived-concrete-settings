from pathlib import Path

from concrete_settings import Setting
from concrete_settings.contrib.sources import PythonSource
from concrete_settings.sources import get_source


def S(name: str, type_hint=str) -> Setting:
    """A helper function which creates a setting and assigns it a name."""
    s = Setting(type_hint=type_hint)
    s.__set_name__(s, name)
    return s


def test_get_python_file_returns_python_source():
    src = get_source('/test/settings.py')
    assert isinstance(src, PythonSource)


def test_json_source_has_expected_path(fs):
    fs.create_file('/test/settings.py', contents='{}')
    pysrc = get_source('/test/settings.py')
    assert pysrc.path == '/test/settings.py'


def test_json_source_read_int_value():
    tests_dir = Path(__file__).parent
    pysrc = get_source(str(tests_dir / 'fixtures/python_settings.py'))
    assert pysrc.read(S('DEBUG'))


# def test_json_source_read_float_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": 10.25}')
#     jsrc = get_source('/test/settings.json')
#     assert jsrc.read(S('A')) == 10.25


# def test_json_source_read_str_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": "abc"}')
#     jsrc = get_source('/test/settings.json')
#     assert jsrc.read(S('A')) == "abc"


# def test_json_source_read_null_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": null}')
#     jsrc = get_source('/test/settings.json')
#     assert jsrc.read(S('A')) is None


# def test_json_source_read_array_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": [1, 2, 3]}')
#     jsrc = get_source('/test/settings.json')
#     assert jsrc.read(S('A')) == [1, 2, 3]


# def test_json_source_read_object_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": {"B": 10}}')
#     jsrc = get_source('/test/settings.json')
#     assert jsrc.read(S('A')) == {"B": 10}


# def test_json_source_read_nested_object_value(fs):
#     fs.create_file('/test/settings.json', contents='{"A": {"B": 10}}')
#     jsrc = get_source('/test/settings.json')
#     assert jsrc.read(S('B'), parents=('A',)) == 10
