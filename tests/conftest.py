import pytest
import random

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
