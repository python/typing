"""
Tests callable assignability with non-constant parameter mapping.

Specification: https://typing.readthedocs.io/en/latest/spec/callables.html#assignability-rules-for-callables

This case is currently rejected by type checkers but appears to be
allowed by the typing spec, since all valid calls are accepted.
"""

from typing import Protocol


class Interval: ...


class Make(Protocol):
    def __call__(self, /, lower: float, upper: float) -> Interval: ...


def make_impl(
    string_or_lower: str | float | None = None,
    /,
    lower: float | None = None,
    upper: float | None = None,
) -> Interval: ...


def test() -> None:
    f: Make = make_impl  # OK
