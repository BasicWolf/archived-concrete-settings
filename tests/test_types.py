import typing

from concrete_settings.types import type_hints_equal


def test_type_hint_equals_for_builtins():
    assert type_hints_equal(int, int)


def test_type_hint_equals_for_annotations():
    assert type_hints_equal(typing.List, typing.List)


def test_type_hint_equals_for_builtin_and_annotation():
    assert type_hints_equal(list, typing.List)
    assert type_hints_equal(typing.List, list)
