import pytest

from concrete_settings.docreader import extract_docstrings


@pytest.fixture(scope='module')
def one_cls_setting():
    return """from concrete_settings import ConcreteSettings

class OneCls(ConcreteSettings):
    #: This is doc
    #: For max_speed
    MAX_SPEED = 10"""


def test_one_cls_setting(one_cls_setting):
    import imp

    mymodule = imp.new_module('mymodule')
    exec(one_cls_setting, mymodule.__dict__)
    # breakpoint()
    # extract_docstrings(one_cls_setting)
