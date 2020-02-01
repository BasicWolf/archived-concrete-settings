from concrete_settings import Setting
from concrete_settings.contrib.sources import EnvVarSource
from concrete_settings.sources import get_source


def S(name: str, type_hint=str) -> Setting:
    """A helper function which creates a setting and assigns it a name."""
    s = Setting(type_hint=type_hint)
    s.__set_name__(s, name)
    return s


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


def test_env_source_read_non_existing_setting_returns_setting_value():
    esrc = get_source(EnvVarSource())
    setting = S('NOT_EXISTS')
    setting.value = 'some default value'
    assert esrc.read(setting) == 'some default value'
