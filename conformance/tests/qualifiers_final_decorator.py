"""
Tests the @final decorator.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/qualifiers.html#final

from typing import final, overload
from _qualifiers_final_decorator import Base3, Base4

# > A type checker should prohibit any class decorated with @final from being
# > subclassed and any method decorated with @final from being overridden in a
# > subclass. The method decorator version may be used with all of instance
# > methods, class methods, static methods, and properties.


@final
class Base1:
    ...


class Derived1(Base1):  # E: Cannot inherit from final class "Base"
    ...


class Base2:
    @final
    def method1(self) -> None:
        pass

    @final
    @classmethod
    def method2(cls) -> None:
        pass

    @final
    @staticmethod
    def method3() -> None:
        pass

    # > For overloaded methods, @final should be placed on the implementation.

    @overload
    def method4(self, x: int) -> int:
        ...

    @overload
    def method4(self, x: str) -> str:
        ...

    @final
    def method4(self, x: int | str) -> int | str:
        return 0


class Derived2(Base2):
    def method1(self) -> None:  # E
        pass

    @classmethod
    def method2(cls) -> None:  # E
        pass

    @staticmethod
    def method3() -> None:  # E
        pass

    @overload
    def method4(self, x: int) -> int:
        ...

    @overload
    def method4(self, x: str) -> str:
        ...

    def method4(self, x: int | str) -> int | str:  # E
        return 0


class Derived3(Base3):
    @overload
    def method(self, x: int) -> int:
        ...

    @overload
    @final  # E: should be applied only to implementation
    def method(self, x: str) -> str:
        ...

    def method(self, x: int | str) -> int | str:  # E
        return 0


class Derived4(Base4):
    @overload
    def method(self, x: int) -> int:
        ...

    @overload
    def method(self, x: str) -> str:
        ...

    def method(self, x: int | str) -> int | str:  # E
        return 0


class Base5_1:
    ...


class Base5_2:
    @final
    def method(self, v: int) -> None:
        ...


# Test multiple inheritance case.
class Derived5(Base5_1, Base5_2):
    def method(self) -> None:  # E
        ...


# > It is an error to use @final on a non-method function.


@final
def func1() -> int:  # E: not allowed on non-method function.
    return 0
