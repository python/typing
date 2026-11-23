"""
Tests Boolean combinations of version, platform, and implementation checks.
"""

# Specification: https://typing.python.org/en/latest/spec/directives.html#version-and-platform-checks

import sys
from typing import assert_type


def test_not(a: int, b: str) -> None:
    # > Type checkers should support combining these checks with:
    # > * A ``not`` unary operator
    error: int = 0
    selected: int | str
    if not (sys.platform == "bogus_platform"):
        error = "reachable"  # E
        selected = a
    else:
        error = "unreachable"
        selected = b
    assert_type(selected, int)

    if not (sys.version_info >= (3, 8)):
        error = "unreachable"
    else:
        error = "reachable"  # E

    if not (sys.platform in ("bogus_platform",)):
        error = "reachable"  # E
    else:
        error = "unreachable"


def test_and(a: int, b: str) -> None:
    # > * An ``and`` or ``or`` binary operator
    error: int = 0
    selected: int | str
    if sys.version_info >= (3, 8) and sys.platform != "bogus_platform":
        error = "reachable"  # E
        selected = a
    else:
        error = "unreachable"
        selected = b
    assert_type(selected, int)

    if sys.version_info >= (3, 8) and sys.platform == "bogus_platform":
        error = "unreachable"
    else:
        error = "reachable"  # E
    if sys.version_info < (3, 8) and sys.platform != "bogus_platform":
        error = "unreachable"
    else:
        error = "reachable"  # E
    if sys.version_info < (3, 8) and sys.platform == "bogus_platform":
        error = "unreachable"
    else:
        error = "reachable"  # E


def test_or(a: int, b: str) -> None:
    error: int = 0
    selected: int | str
    if sys.version_info < (3, 8) or sys.platform == "bogus_platform":
        error = "unreachable"
        selected = b
    else:
        error = "reachable"  # E
        selected = a
    assert_type(selected, int)

    if sys.version_info >= (3, 8) or sys.platform == "bogus_platform":
        error = "reachable"  # E
    else:
        error = "unreachable"
    if sys.version_info < (3, 8) or sys.platform != "bogus_platform":
        error = "reachable"  # E
    else:
        error = "unreachable"
    if sys.version_info >= (3, 8) or sys.platform != "bogus_platform":
        error = "reachable"  # E
    else:
        error = "unreachable"


def test_nested_elif(a: int, b: str) -> None:
    error: int = 0
    selected: int | str
    if not (sys.version_info >= (3, 8) or sys.platform != "bogus_platform"):
        error = "unreachable"
        selected = b
    elif sys.version_info >= (3, 8) and (
        sys.platform == "bogus_platform" or sys.platform != "bogus_platform"
    ):
        error = "reachable"  # E
        selected = a
    else:
        error = "unreachable"
        selected = b
    assert_type(selected, int)


def test_implementation_combinations(a: int, b: str) -> None:
    error: int = 0
    selected: int | str
    if sys.implementation.name == "cpython" and (
        sys.implementation.version >= (3, 12)
        and not (sys.platform in ["bogus_platform"])
    ):
        error = "reachable"  # E
        selected = a
    elif sys.implementation.name == "micropython" and (
        sys.implementation.version >= (1, 24)
    ):
        error = "unreachable"
        selected = b
    else:
        error = "unreachable"
        selected = b
    assert_type(selected, int)

    if not (sys.implementation.name in {"cpython", "pypy"}):
        error = "unreachable"
    else:
        error = "reachable"  # E
    if sys.implementation.name != "cpython" or (
        sys.implementation.version < (3, 12)
    ):
        error = "unreachable"
    else:
        error = "reachable"  # E
