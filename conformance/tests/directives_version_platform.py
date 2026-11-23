"""
Tests checking the version or platform.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/directives.html#version-and-platform-checking

import os
import sys
from typing import assert_type

def test(a: int, b: str):
    val1: int | str
    if sys.version_info >= (3, 8):
        val1 = a
    else:
        val1 = b

    assert_type(val1, int)

    val2: int | str
    if sys.version_info >= (3, 8, 0):
        val2 = a
    else:
        val2 = b

    assert_type(val2, int)  # E?: Support for three-element sys.version_info is optional.

    if sys.version_info < (3, 8):
        val3 = ""
    else:
        val4 = ""

    this_raises = val3  # E: `val3` is undefined
    does_not_raise = val4  # should not error

    val5: int | str
    if sys.version_info < (3, 100, 0):
        val5 = a
    else:
        val5 = b

    assert_type(val5, int)  # E?: Support for three-element sys.version_info is optional.


    if sys.platform == "bogus_platform":
        val6 = ""
    else:
        val7 = ""

    this_raises = val6  # E: `val6` is undefined
    does_not_raise = val7  # should not error

    if sys.platform != "bogus_platform":
        val8 = ""
    else:
        val9 = ""

    does_not_raise = val8  # should not error
    this_raises = val9  # E: `val9` is undefined

    if os.name == "bogus_os":
        val10 = ""
    else:
        val11 = ""

    this_raises = val10  # E?: `val10` is undefined, but support for `os.name` is optional
    does_not_raise = val11  # E? should not error if `os.name` control flow is supported, but might be flagged as possibly undefined otherwise

    if os.name != "bogus_os":
        val12 = ""
    else:
        val13 = ""

    does_not_raise = val12  # E?: should not error if `os.name` control flow is supported, but might be flagged as possibly undefined otherwise
    this_raises = val13  # E?: `val13` is undefined, but support for `os.name` is optional


def test_version_boundaries(a: int, b: str) -> None:
    # The conformance suite targets Python 3.12.
    # > Required support is limited to comparisons against literal two-element tuples.
    error: int = 0
    at_boundary: int | str
    if sys.version_info >= (3, 12):
        error = "reachable"  # E: The boundary is inclusive.
        at_boundary = a
    else:
        error = "unreachable"
        at_boundary = b
    assert_type(at_boundary, int)

    below_boundary: int | str
    if sys.version_info < (3, 12):
        error = "unreachable"
        below_boundary = b
    else:
        error = "reachable"  # E: The boundary is exclusive.
        below_boundary = a
    assert_type(below_boundary, int)


def test_version_elif(a: int, b: str) -> None:
    error: int = 0
    selected: int | str
    if sys.version_info >= (3, 100):
        error = "unreachable"
        selected = b
    elif sys.version_info < (3, 8):
        error = "unreachable"
        selected = b
    elif sys.version_info >= (3, 8):
        error = "reachable"  # E: Only this branch is reachable.
        selected = a
    else:
        error = "unreachable"
        selected = b
    assert_type(selected, int)
