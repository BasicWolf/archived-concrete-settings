import pytest
from concrete_settings import Setting, Settings
from concrete_settings import sources
from concrete_settings.sources import strategies

from .utils import Match


def test_get_source_fail_for_unknown_source():
    with pytest.raises(sources.NoSuitableSourceFoundError):
        assert sources.get_source('/test/dummy')


#
# StringSourceMixin
#


def test_string_source_mixin_convert_int_value():
    assert sources.StringSourceMixin.convert_value('10', int) == 10


def test_string_source_mixin_convert_float_value():
    assert sources.StringSourceMixin.convert_value('10.25', float) == 10.25


@pytest.mark.parametrize('true_str', ('true', 'True', 'TRUE'))
def test_string_source_mixin_convert_true_value(true_str):
    assert sources.StringSourceMixin.convert_value(true_str, bool) is True


@pytest.mark.parametrize('false_str', ('false', 'False', 'FALSE'))
def test_string_source_mixin_convert_false_value(false_str):
    assert sources.StringSourceMixin.convert_value(false_str, bool) is False


#
# Dict source
#


def S(name: str, type_hint=str) -> Setting:
    s = Setting(type_hint=type_hint)
    s.__set_name__(s, name)
    return s


def test_get_source_for_dict_retuns_dict_source():
    dsrc = sources.get_source({'a': 10})
    assert isinstance(dsrc, sources.Source)


def test_dict_source_one_level_values():
    dsrc = sources.get_source({'a': 10, 'b': 20})
    assert dsrc.read(S('a')) == 10
    assert dsrc.read(S('b')) == 20


def test_dict_source_two_levels_nested_dicts_values():
    dsrc = sources.get_source({'a': 10, 'c': {'d': 30}})
    assert dsrc.read(S('a')) == 10
    assert dsrc.read(S('c')) == {'d': 30}
    assert dsrc.read(S('d'), parents=('c',)) == 30


#
# Updating
#
def test_update_source_is_not_called_on_empty(mocker):
    class S(Settings):
        pass

    s = S()
    src_mock = mocker.Mock(spec=sources.Source)

    s.update(src_mock)
    src_mock.read.assert_not_called()


def test_update_top_level_setting_source_is_called(mocker):
    class S(Settings):
        T: int = 10

    s = S()
    src_mock = mocker.Mock(spec=sources.Source)
    src_mock = mocker.Mock(spec=sources.Source)
    src_mock.read = mocker.MagicMock(return_value=10)

    s.update(src_mock)
    src_mock.read.assert_called_with(Match(lambda arg: arg.name == 'T'), ())


def test_update_top_level_setting_from_source(mocker):
    class S(Settings):
        T: int = 10

    s = S()
    src_mock = mocker.Mock(spec=sources.Source)
    src_mock = mocker.Mock(spec=sources.Source)
    src_mock.read = mocker.MagicMock(side_effect=lambda *ignore: 10)

    s.update(src_mock)
    assert s.is_valid()
    assert s.T == 10


def test_update_nested_setting_source_is_called(mocker):
    class S(Settings):
        T: int = 10

    class S1(Settings):
        NESTED_S = S()

    s1 = S1()
    src_mock = mocker.Mock(spec=sources.Source)
    src_mock.read = mocker.MagicMock()

    s1.update(src_mock)

    src_mock.read.assert_called_once_with(
        Match(lambda arg: arg.name == 'T'), ('NESTED_S',)
    )


def test_update_nested_setting_from_source(mocker):
    class S(Settings):
        T: int = 10

    class S1(Settings):
        NESTED_S = S()

    s1 = S1()
    src_mock = mocker.Mock(spec=sources.Source)
    src_mock.read = mocker.MagicMock(return_value=20)

    s1.update(src_mock)
    assert s1.is_valid()
    assert s1.NESTED_S.T == 20


def test_update_strategy_overwrite_explicit():
    class S(Settings):
        T: list = [1, 2]

    s = S()
    s.update({'T': [3, 4]}, strategies={'T': strategies.overwrite})
    assert s.T == [3, 4]


def test_update_strategy_default_is_overwrite():
    class S(Settings):
        T: list = [1, 2]

    s = S()
    s.update({'T': [3, 4]})
    assert s.T == [3, 4]


def test_update_strategy_append():
    class S(Settings):
        LST: list = [1, 2]
        TPL: tuple = (1, 2)
        STR: str = '12'
        INT: int = 12

    s = S()
    s.update(
        {'LST': [3, 4], 'TPL': (3, 4), 'STR': '34', 'INT': 34},
        strategies={
            'LST': strategies.append,
            'TPL': strategies.append,
            'STR': strategies.append,
            'INT': strategies.append,
        },
    )

    assert s.LST == [1, 2, 3, 4]
    assert s.TPL == (1, 2, 3, 4)
    assert s.STR == '1234'
    assert s.INT == 46
