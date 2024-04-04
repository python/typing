"""
Tests Callable annotation and parameter annotations for "def" statements.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/callables.html#callable

from typing import Callable, assert_type


def func1(cb: Callable[[int, str], list[str]]) -> None:
    assert_type(cb(1, ""), list[str])

    cb(1)  # E
    cb(1, 2)  # E
    cb(1, "", 1)  # E
    # Mypy reports two errors, one for each kwarg.
    cb(a=1, b="")  # E: bad kwarg 'a'  # E?: bad kwarg 'b'


def func2(cb: Callable[[], dict[str, str]]) -> None:
    assert_type(cb(), dict[str, str])

    cb(1)  # E


# > It is possible to declare the return type of a callable without specifying
# > the call signature by substituting a literal ellipsis (three dots) for the
# > list of arguments.
def func3(cb: Callable[..., list[str]]):
    assert_type(cb(), list[str])
    assert_type(cb(""), list[str])
    assert_type(cb(1, ""), list[str])


def func4(*args: int, **kwargs: int) -> None:
    assert_type(args, tuple[int, ...])
    assert_type(kwargs, dict[str, int])


v1: Callable[int]  # E
v2: Callable[int, int]  # E
v3: Callable[[], [int]]  # E
v4: Callable[int, int, int]  # E
v5: Callable[[...], int]  # E
