"""
Tests the handling and enforcement of TypeVar variance.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/generics.html#variance

from typing import TypeVar, Generic
from collections.abc import Iterable, Iterator

# > To facilitate the declaration of container types where covariant or
# > contravariant type checking is acceptable, type variables accept
# > keyword arguments covariant=True or contravariant=True. At most one of
# > these may be passed.
X1 = TypeVar("X1", covariant=True, contravariant=True)  # Type error


T_co = TypeVar("T_co", covariant=True)


class ImmutableList(Generic[T_co]):
    def __init__(self, items: Iterable[T_co]) -> None:
        ...

    def __iter__(self) -> Iterator[T_co]:
        ...


class Employee:
    ...


class Manager(Employee):
    ...


managers: ImmutableList[Manager] = ImmutableList([Manager()])
employees: ImmutableList[Employee] = managers  # OK


E = TypeVar("E", bound=Employee)


def dump_employee(e: E) -> E:
    return e


dump_employee(Manager())  # OK


B_co = TypeVar("B_co", covariant=True)


# > Variance is only applicable to generic types; generic functions do not
# > have this property. The latter should be defined using only type variables
# > without covariant or contravariant keyword arguments.
def bad_func(x: list[B_co]) -> B_co:  # Type checker error
    ...
