import tempfile
import random

import pytest


import factory
from factory import fuzzy


seed = random.randint(1, 1e9)
print(f"Running tests with seed: {seed:0>10}")
factory.fuzzy.reseed_random(seed)


@pytest.fixture
def rint():
    return fuzzy.FuzzyInteger(-10e10, 10e10).fuzz()


@pytest.fixture
def rstr():
    return fuzzy.FuzzyText(length=100).fuzz()


@pytest.fixture
def mock_module(mocker):
    import imp
    import sys

    tmp_files = []

    def _make_module(name, code, path=None):
        mod = imp.new_module(name)

        if path:
            mod.__file__ = path
        else:
            tmp_file = tempfile.NamedTemporaryFile(mode='w+', prefix=f'tmp_{name}', suffix='.py')
            tmp_file.write(code)
            tmp_file.flush()
            mod.__file__ = tmp_file.name
            tmp_files.append(tmp_file)
        sys.modules[name] = mod
        exec(code, mod.__dict__)

    yield _make_module

    for f in tmp_files:
        f.close()
