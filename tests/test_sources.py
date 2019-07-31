import pytest
from concrete_settings import Settings
from concrete_settings.sources import get_source, DictSource, NoSuitableSourceFoundError


def test_get_source_fail_for_unknown_source():
    with pytest.raises(NoSuitableSourceFoundError):
        assert get_source('/test/dummy')


#
# Dict source
#


def test_get_source_for_dict_retuns_dict_source():
    dsrc = get_source({'a': 10})
    assert isinstance(dsrc, DictSource)


def test_dict_source_one_level_values():
    dsrc = get_source({'a': 10, 'b': 20})
    assert dsrc.read('a') == 10
    assert dsrc.read('b') == 20


def test_dict_source_two_levels_nested_dicts_values():
    dsrc = get_source({'a': 10, 'c': {'d': 30}})
    assert dsrc.read('a') == 10
    assert dsrc.read('c') == {'d': 30}
    assert dsrc.read('d', parents=('c',)) == 30
