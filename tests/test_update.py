from concrete_settings import Settings
from concrete_settings.sources import Source

from .utils import Match


def test_update_source_is_not_called_on_empty(mocker):
    class S(Settings):
        pass

    s = S()
    src_mock = mocker.Mock(spec=Source)

    s.update(src_mock)
    src_mock.read.assert_not_called()


def test_update_top_level_setting_source_is_called(mocker):
    class S(Settings):
        T: int = 10

    s = S()
    src_mock = mocker.Mock(spec=Source)
    src_mock = mocker.Mock(spec=Source)
    src_mock.read = mocker.MagicMock(return_value=10)

    s.update(src_mock)
    src_mock.read.assert_called_with(Match(lambda arg: arg.name == 'T'), ())


def test_update_top_level_setting_from_source(mocker):
    class S(Settings):
        T: int = 10

    s = S()
    src_mock = mocker.Mock(spec=Source)
    src_mock = mocker.Mock(spec=Source)
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
    src_mock = mocker.Mock(spec=Source)
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
    src_mock = mocker.Mock(spec=Source)
    src_mock.read = mocker.MagicMock(return_value=20)

    s1.update(src_mock)
    assert s1.is_valid()
    assert s1.NESTED_S.T == 20
