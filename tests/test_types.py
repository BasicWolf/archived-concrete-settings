from typing import List, Any

import pytest

from concrete_settings.types import type_hints_equal, Undefined, GuessSettingType


def test_type_hint_equals_for_builtins():
    assert type_hints_equal(int, int)


def test_type_hint_equals_for_annotations():
    assert type_hints_equal(List, List)


def test_type_hint_equals_for_builtin_and_annotation():
    assert type_hints_equal(list, List)
    assert type_hints_equal(List, list)


def test_guess_type_hint_for_arbitrary_class_returns_any():
    class SomeClass:
        pass

    assert GuessSettingType.guess_type_hint(SomeClass()) is Any


def test_undefined_cannot_be_instantiated():
    with pytest.raises(RuntimeError):
        Undefined()


def test_undefined_is_false():
    assert not Undefined
