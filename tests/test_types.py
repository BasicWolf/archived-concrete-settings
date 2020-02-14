import typing

import pytest

from concrete_settings.types import type_hints_equal, Undefined


def test_type_hint_equals_for_builtins():
    assert type_hints_equal(int, int)


def test_type_hint_equals_for_annotations():
    assert type_hints_equal(typing.List, typing.List)


def test_type_hint_equals_for_builtin_and_annotation():
    assert type_hints_equal(list, typing.List)
    assert type_hints_equal(typing.List, list)


def test_undefined_cannot_be_instantiated():
    with pytest.raises(RuntimeError):
        Undefined()
