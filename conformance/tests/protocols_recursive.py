"""
Tests the handling of recursive protocols.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/protocol.html#recursive-protocols


from typing import Generic, Iterable, Never, Protocol, Self, TypeVar, assert_type

T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)


class Traversable(Protocol):
    def leaves(self) -> Iterable["Traversable"]:
        ...


class SimpleTree:
    def leaves(self) -> list["SimpleTree"]:
        return []


root: Traversable = SimpleTree()  # OK


class Tree(Generic[T]):
    def leaves(self) -> list["Tree[T]"]:
        return []


def walk(graph: Traversable) -> None:
    pass


tree: Tree[float] = Tree()
walk(tree)  # OK


class ProtoA(Protocol[T_contra, T]):
    def method1(self) -> "ProtoA[T_contra, T]":
        ...

    @classmethod
    def method2(cls, value: T) -> None:
        ...


class ProtoB(Protocol[T_contra, T]):
    def method3(self) -> ProtoA[T_contra, T]:
        ...


class ImplA:
    def method1(self) -> Self:
        return self

    @classmethod
    def method2(cls, value: int) -> None:
        pass


class ImplB:
    def method3(self) -> ImplA:
        return ImplA()

    def method1(self) -> Self:
        return self

    @classmethod
    def method2(cls: type[ProtoB[Never, T]], value: list[T]) -> None:
        pass


def func1(x: ProtoA[Never, T]) -> T:
    ...


v1 = func1(ImplB())
assert_type(v1, list[int])
