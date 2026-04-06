"""
Tests for behavior of nested Optional types collapsing.

Optional[Optional[T]] should behave as Optional[T].
"""

from typing import Optional, assert_type


def test_nested_optional(x: Optional[Optional[int]]) -> None:
    # Should behave like Optional[int]
    assert_type(x, Optional[int])


def test_nested_optional_error(x: Optional[Optional[int]]) -> int:
    return x  # E
