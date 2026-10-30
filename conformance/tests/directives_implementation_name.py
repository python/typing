"""
Tests implementation-name equality and membership checks.

These tests use the suite's Python 3.12 target and default CPython implementation.
"""

# Specification: https://typing.python.org/en/latest/spec/directives.html#version-and-platform-checks

import sys
from typing import assert_type


def test_name_equality(a: int, b: str) -> None:
    # > Default value: ``"cpython"``, unless configured otherwise.
    error: int = 0
    equal: int | str
    if sys.implementation.name == "cpython":
        error = "reachable"  # E
        equal = a
    else:
        error = "unreachable"
        equal = b
    assert_type(equal, int)

    unequal: int | str
    if sys.implementation.name != "cpython":
        error = "unreachable"
        unequal = b
    else:
        error = "reachable"  # E
        unequal = a
    assert_type(unequal, int)

    other: int | str
    if sys.implementation.name == "micropython":
        error = "unreachable"
        other = b
    elif sys.implementation.name != "micropython":
        error = "reachable"  # E
        other = a
    else:
        error = "unreachable"
        other = b
    assert_type(other, int)


def test_name_tuple_membership(a: int, b: str) -> None:
    error: int = 0
    contained: int | str
    if sys.implementation.name in ("cpython", "pypy"):
        error = "reachable"  # E
        contained = a
    else:
        error = "unreachable"
        contained = b
    assert_type(contained, int)

    excluded: int | str
    if sys.implementation.name not in ("cpython",):
        error = "unreachable"
        excluded = b
    else:
        error = "reachable"  # E
        excluded = a
    assert_type(excluded, int)

    if sys.implementation.name in ("micropython",):
        error = "unreachable"
    else:
        error = "reachable"  # E
    if sys.implementation.name not in ("micropython", "pypy"):
        error = "reachable"  # E
    else:
        error = "unreachable"


def test_name_set_membership(a: int, b: str) -> None:
    error: int = 0
    contained: int | str
    if sys.implementation.name in {"cpython", "pypy"}:
        error = "reachable"  # E
        contained = a
    else:
        error = "unreachable"
        contained = b
    assert_type(contained, int)

    excluded: int | str
    if sys.implementation.name not in {"cpython"}:
        error = "unreachable"
        excluded = b
    else:
        error = "reachable"  # E
        excluded = a
    assert_type(excluded, int)

    if sys.implementation.name in {"micropython"}:
        error = "unreachable"
    else:
        error = "reachable"  # E
    if sys.implementation.name not in {"micropython", "pypy"}:
        error = "reachable"  # E
    else:
        error = "unreachable"


def test_name_list_membership(a: int, b: str) -> None:
    error: int = 0
    contained: int | str
    if sys.implementation.name in ["cpython", "pypy"]:
        error = "reachable"  # E
        contained = a
    else:
        error = "unreachable"
        contained = b
    assert_type(contained, int)

    excluded: int | str
    if sys.implementation.name not in ["cpython"]:
        error = "unreachable"
        excluded = b
    else:
        error = "reachable"  # E
        excluded = a
    assert_type(excluded, int)

    if sys.implementation.name in ["micropython"]:
        error = "unreachable"
    else:
        error = "reachable"  # E
    if sys.implementation.name not in ["micropython", "pypy"]:
        error = "reachable"  # E
    else:
        error = "unreachable"
