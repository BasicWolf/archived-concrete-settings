import sys
import pytest


@pytest.fixture(scope='module')
def one_cls_setting():
    return """from concrete_settings import Settings

class OneSettingCls(Settings):
    #: This is doc
    #: For max_speed
    MAX_SPEED = 10"""


def test_one_cls_setting(build_module_mock, one_cls_setting):
    build_module_mock('cls1', one_cls_setting)
    assert (
        sys.modules['cls1'].OneSettingCls.MAX_SPEED.__doc__
        == 'This is doc\nFor max_speed'
    )
