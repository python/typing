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


if TYPE_CHECKING:
    x: int = ""  # E: In a `if TYPE_CHECKING` block, type checkers should report all errors as normal
else:
    x: int = ""  # E? Many type checkers suppress all errors in `else` blocks of `if TYPE_CHECKING`, though this is not currently specified

if not TYPE_CHECKING:
    x: int = ""  # E? Many type checkers suppress all errors in `if not TYPE_CHECKING` blocks, though this is not currently specified
