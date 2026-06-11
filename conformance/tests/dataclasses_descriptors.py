"""
Tests the handling of descriptors within a dataclass.
"""

# This portion of the dataclass spec is under-specified in the documentation,
# but its behavior can be determined from the runtime implementation.

from dataclasses import dataclass
from typing import Any, Generic, TypeVar, assert_type, overload

T = TypeVar("T")


class Desc1:
    @overload
    def __get__(self, __obj: None, __owner: Any) -> "Desc1":
        ...

    @overload
    def __get__(self, __obj: object, __owner: Any) -> int:
        ...

    def __get__(self, __obj: object | None, __owner: Any) -> "int | Desc1":
        raise NotImplementedError

    def __set__(self, __obj: object, __value: int) -> None:
        ...


@dataclass
class DC1:
    y: Desc1 = Desc1()


dc1 = DC1(3)

assert_type(dc1.y, int)
assert_type(DC1.y, Desc1)


class Desc2(Generic[T]):
    @overload
    def __get__(self, instance: None, owner: Any) -> list[T]:
        ...

    @overload
    def __get__(self, instance: object, owner: Any) -> T:
        ...

    def __get__(self, instance: object | None, owner: Any) -> list[T] | T:
        raise NotImplementedError


@dataclass
class DC2:
    x: Desc2[int]
    y: Desc2[str]
    z: Desc2[str] = Desc2()


# Runtime behavior involving non-data descriptors in dataclasses is
# currently under-specified and differs across type checkers and runtime
# implementations.
#
# In particular:
# - DC2.x and DC2.y raise AttributeError at runtime because no descriptor
#   instance is stored in the class dictionary for those fields.
# - dc2.x and dc2.y evaluate to the stored Desc2 instances because
#   non-data descriptors are shadowed by instance attributes.
# - The behavior for z is also subtle because dataclasses access the
#   descriptor during default extraction.
#
# These cases are therefore omitted from the conformance suite until the
# expected behavior is specified more clearly.
