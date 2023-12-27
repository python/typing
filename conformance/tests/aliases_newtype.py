"""
Tests the `typing.NewType` function.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/aliases.html#newtype

from typing import Any, Hashable, Literal, NewType, TypeVar, TypedDict, assert_type

UserId = NewType("UserId", int)

UserId("user")  # Type error: incorrect type
u1: UserId = 42  # Type error: incorrect type
u2: UserId = UserId(42)  # OK

assert_type(UserId(5) + 1, int)

# > Both isinstance and issubclass, as well as subclassing will fail for
# > NewType('Derived', Base) since function objects don’t support these
# > operations.
isinstance(u2, UserId)  # Type error: not allowed in isinstance call


class UserIdDerived(UserId):  # Type error: subclassing not allowed
    pass


# > NewType accepts exactly two arguments: a name for the new unique type,
# > and a base class. The latter should be a proper class (i.e., not a type
# > construct like Union, etc.), or another unique type created by
# > calling NewType.

GoodName = NewType("BadName", int)  # Type error: assigned name does not match

GoodNewType1 = NewType("GoodNewType1", list)

nt1: GoodNewType1[int]  # Type error: NewType cannot be generic

TypeAlias1 = dict[str, str]
GoodNewType2 = NewType("GoodNewType2", TypeAlias1)


BadNewType1 = NewType("BadNewType1", int | str)  # Type error: cannot be generic

T = TypeVar("T")
BadNewType2 = NewType("BadNewType2", list[T])  # Type error: cannot be generic

BadNewType3 = NewType("BadNewType3", Hashable)  # Type error: cannot be protocol

BadNewType4 = NewType("BadNewType4", Literal[7])  # Type error: literal not allowed


class TD1(TypedDict):
    a: int


BadNewType5 = NewType("BadNewType5", TD1)  # Type error: cannot be TypedDict

BadNewType6 = NewType("BadNewType6", GoodNewType1)  # Type error: cannot be NewType

BadNewType7 = NewType("BadNewType7", int, int)  # Type error: too many arguments

BadNewType8 = NewType("BadNewType8", Any)  # Type error: cannot be Any
