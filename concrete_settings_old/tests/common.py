import random

import factory
from factory.fuzzy import FuzzyInteger, FuzzyFloat, FuzzyText


seed = random.randint(1, 1e9)
print(f'Running tests with seed: {seed:0>10}')
factory.fuzzy.reseed_random(seed)


INT_VAL: int = FuzzyInteger(-10e10, 10e10).fuzz()
FLOAT_VAL: float = FuzzyFloat(-10e10, 10e10).fuzz()
STR_VAL: str = FuzzyText(length=FuzzyInteger(1, 255).fuzz()).fuzz()

STR_CONST: str = 'HELLO DESCRIPTION'
