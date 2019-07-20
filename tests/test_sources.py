import pytest
from concrete_settings.sources import get_source, DictSource, NoSuitableSourceFoundError


def test_get_dict_source():
    assert isinstance(get_source({}), DictSource)


def test_get_source_fail_for_unknown_source():
    with pytest.raises(NoSuitableSourceFoundError):
        assert get_source('/test/dummy')
