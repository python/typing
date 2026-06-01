"""
Tests the handling of descriptors within a dataclass.
"""

# This portion of the dataclass spec is under-specified in the documentation,
# but the expected behavior follows the runtime implementation.
# See https://github.com/python/typing/issues/2259.

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


# ``Desc2`` is a non-data descriptor (it implements only ``__get__``). A
# non-data descriptor is shadowed by an instance's ``__dict__``, so its
# ``__get__`` is not invoked for attributes that the dataclass ``__init__``
# stores on the instance. Such attributes keep the value that was assigned to
# them. The descriptor protocol only runs for attributes that are present in the
# class namespace.


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
    z: Desc2[str] = Desc2()  # E?: a non-data descriptor default may be rejected


# ``x`` and ``y`` are not present in the class namespace, so accessing them on
# the class is an ``AttributeError`` at runtime; a type checker may report an
# error here. ``z`` is present in the class namespace, so class access runs
# ``Desc2.__get__(None)`` and yields ``list[str]``.
assert_type(DC2.x, Desc2[int])  # E?
assert_type(DC2.y, Desc2[str])  # E?
assert_type(DC2.z, list[str])

# All three attributes are stored on the instance by ``__init__``. Because
# ``Desc2`` is a non-data descriptor, the instance ``__dict__`` shadows it and
# ``__get__`` never runs, so each attribute keeps the assigned ``Desc2`` object
# (even ``z``, which is also present in the class namespace).
dc2 = DC2(Desc2(), Desc2(), Desc2())
assert_type(dc2.x, Desc2[int])
assert_type(dc2.y, Desc2[str])
assert_type(dc2.z, Desc2[str])
