"""
Tests for annotating instance and class methods.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/annotations.html#annotating-instance-and-class-methods

from typing import TypeVar, assert_type


T = TypeVar("T", bound="A")


class A:
    def copy(self: T) -> T:
        return self

    @classmethod
    def factory(cls: type[T]) -> T:
        return cls()


class B(A):
    ...


assert_type(A().copy(), A)
assert_type(A.factory(), A)

assert_type(B().copy(), B)
assert_type(B.factory(), B)
