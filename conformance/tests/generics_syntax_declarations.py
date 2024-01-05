"""
Validates the type parameter syntax introduced in PEP 695.
"""

# Specification: https://peps.python.org/pep-0695/#type-parameter-declarations


# This generic class is parameterized by a TypeVar T, a
# TypeVarTuple Ts, and a ParamSpec P.
from typing import Generic, ParamSpec, Protocol, TypeVar, TypeVarTuple, assert_type


class ChildClass[T, *Ts, **P]:
    assert_type(T, TypeVar)
    assert_type(Ts, TypeVarTuple)
    assert_type(P, ParamSpec)


class ClassA[T](Generic[T]):  # Runtime error
    ...


class ClassB[S, T](Protocol):  # OK
    ...


class ClassC[S, T](Protocol[S, T]):  # Type error
    ...


class ClassD[T: str]:
    def method1(self, x: T):
        x.capitalize()  # OK
        x.is_integer()  # Type error


class ClassE[T: dict[str, int]]:  # OK
    pass


class ClassF[T: "ForwardReference"]:  # OK
    ...


class ClassG[V]:
    class ClassD[T: dict[str, V]]:  # Type error: generic type not allowed
        ...


class ClassH[T: [str, int]]:  # Type error: illegal expression form
    ...


class ClassI[AnyStr: (str, bytes)]:  # OK
    ...


class ClassJ[T: ("ForwardReference", bytes)]:  # OK
    ...


class ClassK[T: ()]:  # Type error: two or more types required
    ...


class ClassL[T: (str,)]:  # Type error: two or more types required
    ...


t1 = (bytes, str)


class ClassM[T: t1]:  # Type error: literal tuple expression required
    ...


class ClassN[T: (3, bytes)]:  # Type error: invalid expression form
    ...


class ClassO[T: (list[S], str)]:  # Type error: generic type
    ...


class ForwardReference:
    ...
