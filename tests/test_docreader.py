import sys
import pytest


@pytest.fixture(scope='module')
def test_settings_with_docs_module():
    return """
from concrete_settings import Settings

class TestSettings(Settings):
    #: This is doc
    #: For max_speed
    MAX_SPEED = 10
"""


def test_attribute_setting_doc_read(build_module_mock, test_settings_with_docs_module):
    build_module_mock('test_settings_module', test_settings_with_docs_module)
    assert (
        sys.modules['test_settings_module'].TestSettings.MAX_SPEED.__doc__
        == 'This is doc\nFor max_speed'
    )
