import os
import random
import tempfile

import factory
import pytest
from factory import fuzzy
from pyfakefs.fake_filesystem_unittest import Patcher

from concrete_settings import Validator
from concrete_settings.exceptions import ValidationError

seed = random.randint(1, 1e9)
print(f"Running tests with seed: {seed:0>10}")
factory.random.reseed_random(seed)

# Do not allow fakefs patcher to scan Django
# fixes ImproperlyConfigured situations
Patcher.SKIPNAMES.add('django')


@pytest.fixture
def v_int():
    return fuzzy.FuzzyInteger(-10e10, 10e10).fuzz()


@pytest.fixture
def v_str():
    return fuzzy.FuzzyText(length=100).fuzz()


@pytest.fixture
def build_module_mock(mocker):
    import sys
    import types

    tmp_files = []

    def _make_module(name, code='', path=None):
        module = types.ModuleType(name)

        if path:
            module.__file__ = path
        else:
            tmp_file = tempfile.NamedTemporaryFile(
                mode='w+', prefix=f'tmp_{name}', suffix='.py', delete=False
            )
            tmp_file.write(code)
            tmp_file.flush()
            tmp_file.close()
            module.__file__ = tmp_file.name
            tmp_files.append(tmp_file)
        sys.modules[name] = module
        exec(code, module.__dict__)
        return module

    yield _make_module

    for f in tmp_files:
        os.remove(f.name)


@pytest.fixture
def is_positive():
    def is_positive(val, **kwargs):
        if val <= 0:
            raise ValidationError('Value should be positive')

    return is_positive


@pytest.fixture
def is_less_that_10():
    def is_less_that_10(val, **kwargs):
        if val >= 10:
            raise ValidationError('Value should be less that 10')

    return is_less_that_10


@pytest.fixture
def DummyValidator():
    class DummyValidator(Validator):
        def __call__(self, value, **kwargs):
            pass

    return DummyValidator
