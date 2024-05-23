"""
Tests the handling of a ParamSpec specialization.
"""


from typing import Callable, Concatenate, Generic, ParamSpec, TypeVar


T = TypeVar("T")
P1 = ParamSpec("P1")
P2 = ParamSpec("P2")


class ClassA(Generic[T, P1]):
    f: Callable[P1, int]
    x: T


class ClassB(ClassA[T, P1], Generic[T, P1, P2]):
    f1: Callable[P1, int]
    f2: Callable[P2, int]
    x: T


def func20(x: ClassA[int, P2]) -> str:  # OK
    return ""


def func21(x: ClassA[int, Concatenate[int, P2]]) -> str:  # OK
    return ""


def func22(x: ClassB[int, [int, bool], ...]) -> str:  # OK
    return ""


def func23(x: ClassA[int, ...]) -> str:  # OK
    return ""


def func24(x: ClassB[int, [], []]) -> str:  # OK
    return ""


def func25(x: ClassA[int, int]) -> str:  # E
    return ""


class ClassC(Generic[P1]):
    f: Callable[P1, int]


def func30(x: ClassC[[int, str, bool]]) -> None:  # OK
    x.f(0, "", True)  # OK
    x.f("", "", True)  # E
    x.f(0, "", "")  # E


def func31(x: ClassC[int, str, bool]) -> None:  # OK
    x.f(0, "", True)  # OK
    x.f("", "", True)  # E
    x.f(0, "", "")  # E
