from pathlib import Path

from concrete_settings import Setting
from concrete_settings.contrib.sources import PythonSource
from concrete_settings.sources import get_source

MY_DIR = Path(__file__).parent
PYTHON_SOURCE_PATH = str(MY_DIR / 'python_settings_fixture.py')


def S(name: str, type_hint=str) -> Setting:
    """A helper function which creates a setting and assigns it a name."""
    s = Setting(type_hint=type_hint)
    s.__set_name__(s, name)
    return s


def test_get_python_file_returns_python_source():
    src = get_source('/test/settings.py')
    assert isinstance(src, PythonSource)


def test_python_source_has_expected_path(fs):
    fs.create_file('/test/settings.py', contents='{}')
    src = get_source('/test/settings.py')
    assert src.path == '/test/settings.py'


def test_python_source_read_int_value():
    src = get_source(PYTHON_SOURCE_PATH)
    assert src.read(S('DEBUG'))


def test_python_source_read_float_value():
    src = get_source(PYTHON_SOURCE_PATH)
    assert src.read(S('FLOAT')) == 10.25


def test_python_source_read_str_value():
    src = get_source(PYTHON_SOURCE_PATH)
    assert src.read(S('STRING')) == 'abc'


def test_python_source_read_null_value():
    src = get_source(PYTHON_SOURCE_PATH)
    assert src.read(S('NULL')) is None


def test_python_source_read_array_value():
    src = get_source(PYTHON_SOURCE_PATH)
    assert src.read(S('LIST')) == [1, 2, 3]


def test_python_source_read_object_value():
    src = get_source(PYTHON_SOURCE_PATH)
    assert src.read(S('DICT')) == {'KEY': 'VALUE'}


def test_python_source_read_nested_object_value():
    src = get_source(PYTHON_SOURCE_PATH)
    assert src.read(S('PORT'), parents=('DATABASE',)) == 1234


def test_python_source_read_non_existing_setting_returns_setting_value():
    src = get_source(PYTHON_SOURCE_PATH)
    setting = S('NOT_EXISTS')
    setting.value = 'some default value'
    assert src.read(setting) == 'some default value'
