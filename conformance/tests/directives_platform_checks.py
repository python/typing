"""
Tests platform comparisons, literal containment, and prefix checks.
"""

# Specification: https://typing.python.org/en/latest/spec/directives.html#version-and-platform-checks

import sys
from typing import assert_type


def test_equality(a: int, b: str) -> None:
    error: int = 0
    equal: int | str
    if sys.platform == "bogus_platform":
        error = "unreachable"
        equal = b
    else:
        error = "reachable"  # E
        equal = a
    assert_type(equal, int)

    unequal: int | str
    if sys.platform != "bogus_platform":
        error = "reachable"  # E
        unequal = a
    else:
        error = "unreachable"
        unequal = b
    assert_type(unequal, int)


def test_startswith(a: int, b: str) -> None:
    error: int = 0
    empty_prefix: int | str
    if sys.platform.startswith(""):
        error = "reachable"  # E: Every platform starts with the empty prefix.
        empty_prefix = a
    else:
        error = "unreachable"
        empty_prefix = b
    assert_type(empty_prefix, int)

    unknown_prefix: int | str
    if sys.platform.startswith("bogus_platform"):
        error = "unreachable"
        unknown_prefix = b
    else:
        error = "reachable"  # E
        unknown_prefix = a
    assert_type(unknown_prefix, int)


def test_versioned_platform_prefix() -> None:
    error: int = 0
    if sys.platform == "freebsd13":
        if sys.platform.startswith("freebsd"):
            error = "reachable"  # E[freebsd_match]
        else:
            error = "unreachable"
        if sys.platform.startswith("linux"):
            error = "unreachable"
        else:
            error = "reachable"  # E[freebsd_nonmatch]
    else:
        error = "reachable"  # E[freebsd_match]
        error = "reachable"  # E[freebsd_nonmatch]


def test_tuple_membership(a: int, b: str) -> None:
    # > The membership checks ``in`` and ``not in`` only support simple containment
    # > testing with a literal tuple, literal set, or literal list of literal strings.
    error: int = 0
    contained: int | str
    if sys.platform in ("bogus_platform",):
        error = "unreachable"
        contained = b
    else:
        error = "reachable"  # E
        contained = a
    assert_type(contained, int)

    excluded: int | str
    if sys.platform not in ("bogus_platform", "another_bogus_platform"):
        error = "reachable"  # E
        excluded = a
    else:
        error = "unreachable"
        excluded = b
    assert_type(excluded, int)

    # Positive matches are guarded so this file also works on non-Linux targets.
    if sys.platform == "linux":
        if sys.platform in ("linux", "darwin"):
            error = "reachable"  # E[tuple_match]
        else:
            error = "unreachable"
        if sys.platform not in ("linux",):
            error = "unreachable"
        else:
            error = "reachable"  # E[tuple_nonmatch]
    else:
        error = "reachable"  # E[tuple_match]
        error = "reachable"  # E[tuple_nonmatch]


def test_set_membership(a: int, b: str) -> None:
    error: int = 0
    contained: int | str
    if sys.platform in {"bogus_platform"}:
        error = "unreachable"
        contained = b
    else:
        error = "reachable"  # E
        contained = a
    assert_type(contained, int)

    excluded: int | str
    if sys.platform not in {"bogus_platform", "another_bogus_platform"}:
        error = "reachable"  # E
        excluded = a
    else:
        error = "unreachable"
        excluded = b
    assert_type(excluded, int)

    if sys.platform == "linux":
        if sys.platform in {"linux", "darwin"}:
            error = "reachable"  # E[set_match]
        else:
            error = "unreachable"
        if sys.platform not in {"linux"}:
            error = "unreachable"
        else:
            error = "reachable"  # E[set_nonmatch]
    else:
        error = "reachable"  # E[set_match]
        error = "reachable"  # E[set_nonmatch]


def test_list_membership(a: int, b: str) -> None:
    error: int = 0
    contained: int | str
    if sys.platform in ["bogus_platform"]:
        error = "unreachable"
        contained = b
    else:
        error = "reachable"  # E
        contained = a
    assert_type(contained, int)

    excluded: int | str
    if sys.platform not in ["bogus_platform", "another_bogus_platform"]:
        error = "reachable"  # E
        excluded = a
    else:
        error = "unreachable"
        excluded = b
    assert_type(excluded, int)

    if sys.platform == "linux":
        if sys.platform in ["linux", "darwin"]:
            error = "reachable"  # E[list_match]
        else:
            error = "unreachable"
        if sys.platform not in ["linux"]:
            error = "unreachable"
        else:
            error = "reachable"  # E[list_nonmatch]
    else:
        error = "reachable"  # E[list_match]
        error = "reachable"  # E[list_nonmatch]
