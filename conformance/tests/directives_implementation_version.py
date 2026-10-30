"""
Tests the CPython implementation-version default.

These tests use the suite's Python 3.12 target and default CPython implementation.
"""

# Specification: https://typing.python.org/en/latest/spec/directives.html#version-and-platform-checks

import sys
from typing import assert_type


def test_implementation_version(a: int, b: str) -> None:
    # For the default CPython target, use the configured language version.
    error: int = 0
    at_boundary: int | str
    if sys.implementation.version >= (3, 12):
        error = "reachable"  # E
        at_boundary = a
    else:
        error = "unreachable"
        at_boundary = b
    assert_type(at_boundary, int)

    below_boundary: int | str
    if sys.implementation.version < (3, 12):
        error = "unreachable"
        below_boundary = b
    else:
        error = "reachable"  # E
        below_boundary = a
    assert_type(below_boundary, int)

    if sys.implementation.version < (3, 100):
        error = "reachable"  # E
    else:
        error = "unreachable"
    if sys.implementation.version >= (3, 100):
        error = "unreachable"
    else:
        error = "reachable"  # E
