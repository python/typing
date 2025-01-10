"""
Tests errors on invalid `@typing.overload` usage.
"""

from abc import ABC, abstractmethod
from typing import (
    Protocol,
    overload,
)

# > At least two @overload-decorated definitions must be present.
@overload  # E[func1]
def func1() -> None:  # E[func1]: At least two overloads must be present
    ...


def func1() -> None:
    pass


# > The ``@overload``-decorated definitions must be followed by an overload
# > implementation, which does not include an ``@overload`` decorator. Type
# > checkers should report an error or warning if an implementation is missing.
@overload  # E[func2]
def func2(x: int) -> int:  # E[func2]: no implementation
    ...


@overload
def func2(x: str) -> str:
    ...


# > Overload definitions within stub files, protocols, and on abstract methods
# > within abstract base classes are exempt from this check.
class MyProto(Protocol):
    @overload
    def func3(self, x: int) -> int:
        ...


    @overload
    def func3(self, x: str) -> str:
        ...

class MyAbstractBase(ABC):
    @overload
    @abstractmethod
    def func4(self, x: int) -> int:
        ...


    @overload
    @abstractmethod
    def func4(self, x: str) -> str:
        ...

    # A non-abstract method in an abstract base class still requires an
    # implementation:

    @overload  # E[not_abstract]
    def not_abstract(self, x: int) -> int:  # E[not_abstract] no implementation
        ...


    @overload
    def not_abstract(self, x: str) -> str:
        ...


# > If one overload signature is decorated with ``@staticmethod`` or
# > ``@classmethod``, all overload signatures must be similarly decorated. The
# > implementation, if present, must also have a consistent decorator. Type
# > checkers should report an error if these conditions are not met.
class C:
    @overload  # E[func5]
    @staticmethod
    def func5(x: int) -> int:  # E[func5]
        ...

    @overload
    @staticmethod
    def func5(x: str) -> str:  # E[func5]
        ...

    def func5(self, x: int | str) -> int | str:  # E[func5]
        return 1

    @overload  # E[func6]
    @classmethod
    def func6(cls, x: int) -> int:  # E[func6]
        ...

    @overload
    @classmethod
    def func6(cls, x: str) -> str:  # E[func6]
        ...

    def func6(cls, x: int | str) -> int | str:  # E[func6]
        return 1
