"""
Tests the typing.TYPE_CHECKING constant.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/directives.html#type-checking

from typing import TYPE_CHECKING, assert_type


def foo(x: list[int], y: list[str]) -> None:
    z: list[int] | list[str]

    if TYPE_CHECKING:
        z = x
    else:
        z = y

    assert_type(z, list[int])
