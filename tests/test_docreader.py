import pytest

from concrete_settings.docreader import extract_docstrings


@pytest.fixture(scope='module')
def one_cls_setting():
    return """from concrete_settings import Settings

class C(Settings):
    #: This is doc
    #: For max_speed
    MAX_SPEED = 10"""


def test_one_cls_setting(one_cls_setting):
    extract_docstrings(one_cls_setting)
