"""
Tests the handling of builtins.tuple.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/special-types.html#tuples

# > The type of a tuple can be expressed by listing the element types.
from typing import Literal


t1: tuple[int] = (1,)  # OK
t1 = (1, 2)  # Type error
t2: tuple[int, int] = (1, 2)  # OK
t2 = (1,)  # Type error
t2 = (1, "")  # Type error


def func1() -> tuple[Literal[1], Literal[2]]:
    return (1, 2)


# > The empty tuple can be typed as tuple[()].

t10: tuple[()] = ()  # OK
t10 = (1,)  # Type error


def func2() -> list[tuple[()]]:
    return [(), (), ()]


# > Arbitrary-length homogeneous tuples can be expressed using one type and ellipsis.
t20: tuple[int, ...] = ()  # OK
t20 = (1,)  # OK
t20 = (1, 2, 3, 4)  # OK
t20 = (1, 2, 3, "")  # Type error


# The spec isn't clear on this point, but mypy treats tuple[int, ...]
# as incompatible with tuple[int].
def func3(a: tuple[int, ...]):
    t1: tuple[int] = a  # Type error
    t2: tuple[()] = a  # Type error
