"""
Tests for basic usage of generics.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/generics.html#introduction

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar, assert_type

T = TypeVar('T')

# > Generics can be parameterized by using a factory available in
# > ``typing`` called ``TypeVar``.

def first(l: Sequence[T]) -> T:
    return l[0]


def test_first(seq_int: Sequence[int], seq_str: Sequence[str]) -> None:
    assert_type(first(seq_int), int)
    assert_type(first(seq_str), str)

# > ``TypeVar`` supports constraining parametric types to a fixed set of
# > possible types

AnyStr = TypeVar('AnyStr', str, bytes)

def concat(x: AnyStr, y: AnyStr) -> AnyStr:
    return x + y

def test_concat(s: str, b: bytes, a: Any) -> None:
    concat(s, s)  # OK
    concat(b, b)  # OK
    concat(s, b)  # Type error
    concat(b, s)  # Type error

    concat(s, a)  # OK
    concat(a, b)  # OK

# > Specifying a single constraint is disallowed.

BadConstraint1 = TypeVar('BadConstraint', str)  # Type error

# > Note: those types cannot be parameterized by type variables

BadConstraint2 = TypeVar('BadConstraint', str, T)  # Type error

# > Subtypes of types constrained by a type variable should be treated
# > as their respective explicitly listed base types in the context of the
# > type variable.

class MyStr(str): ...

def test_concat_subtype(s: str, b: bytes, a: Any, m: MyStr) -> None:
    assert_type(concat(m, m), str)
    assert_type(concat(m, s), str)
    concat(m, b)  # Type error

    assert_type(concat(m, a), str)
    assert_type(concat(a, m), str)

# Specification: https://typing.readthedocs.io/en/latest/spec/generics.html#user-defined-generic-classes

# > You can include a ``Generic`` base class to define a user-defined class
# > as generic.

from logging import Logger
from collections.abc import Iterable

class LoggedVar(Generic[T]):
    def __init__(self, value: T, name: str, logger: Logger) -> None:
        self.name = name
        self.logger = logger
        self.value = value

    def set(self, new: T) -> None:
        self.log('Set ' + repr(self.value))
        self.value = new

    def get(self) -> T:
        self.log('Get ' + repr(self.value))
        return self.value

    def log(self, message: str) -> None:
        self.logger.info('{}: {}'.format(self.name, message))


def zero_all_vars(vars: Iterable[LoggedVar[int]]) -> None:
    for var in vars:
        var.set(0)
        assert_type(var.get(), int)


# > A generic type can have any number of type variables, and type variables
# > may be constrained.

T = TypeVar('T')
S = TypeVar('S')

class Pair1(Generic[T, S]):
    ...

# > Each type variable argument to ``Generic`` must be distinct.

class Pair2(Generic[T, T]):   # Type error
      ...

# > The ``Generic[T]`` base class is redundant in simple cases where you
# > subclass some other generic class and specify type variables for its
# > parameters.

from collections.abc import Iterator

class MyIter1(Iterator[T]):
    ...

class MyIter2(Iterator[T], Generic[T]):
    ...

def test_my_iter(m1: MyIter1[int], m2: MyIter2[int]):
    assert_type(next(m1), int)
    assert_type(next(m2), int)

# > You can use multiple inheritance with ``Generic``

from collections.abc import Sized, Container

T = TypeVar('T')

class LinkedList(Sized, Generic[T]):
    ...

K = TypeVar('K')
V = TypeVar('V')

class MyMapping(Iterable[tuple[K, V]], Container[tuple[K, V]], Generic[K, V]):
    ...

# > Subclassing a generic class without specifying type parameters assumes
# > ``Any`` for each position.  In the following example, ``MyIterable``
# > is not generic but implicitly inherits from ``Iterable[Any]``::

class MyIterableAny(Iterable):  # Same as Iterable[Any]
    ...

def test_my_iterable_any(m: MyIterableAny):
    assert_type(iter(m), Iterator[Any])

# > Generic metaclasses are not supported

class GenericMeta(type, Generic[T]): ...

class GenericMetaInstance(metaclass=GenericMeta[T]):  # Type error
    ...
