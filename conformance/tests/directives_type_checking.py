"""
Tests the typing.TYPE_CHECKING constant.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/directives.html#type-checking

from typing import TYPE_CHECKING, assert_type


if not TYPE_CHECKING:
    a: int = ""  # E? Many type checkers suppress all errors in `if not TYPE_CHECKING` blocks, though this is not currently specified

if TYPE_CHECKING:
    x: list[int] = ["foo"]  # E: In a `if TYPE_CHECKING` block, type checkers should report all errors as normal
else:
    x: list[str] = [42]  # E? Many type checkers suppress all errors in `else` blocks of `if TYPE_CHECKING`, though this is not currently specified


def foo(x: list[int], y: list[str]) -> None:
    z: list[int] | list[str]

    if TYPE_CHECKING:
        z = x
    else:
        z = y

    assert_type(z, list[int])
