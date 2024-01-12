"""
Tests the handling and enforcement of TypeVar variance.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/generics.html#variance

from typing import Sequence, TypeVar, Generic
from collections.abc import Iterable, Iterator

# > To facilitate the declaration of container types where covariant or
# > contravariant type checking is acceptable, type variables accept
# > keyword arguments covariant=True or contravariant=True. At most one of
# > these may be passed.
X1 = TypeVar("X1", covariant=True, contravariant=True)  # Type error


T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


class ImmutableList(Generic[T_co]):
    def __init__(self, items: Iterable[T_co]) -> None:
        ...

    def __iter__(self) -> Iterator[T_co]:
        ...


class Employee:
    ...


class Manager(Employee):
    ...


managers: ImmutableList[Manager] = ImmutableList([Manager()])
employees: ImmutableList[Employee] = managers  # OK


E = TypeVar("E", bound=Employee)


def dump_employee(e: E) -> E:
    return e


dump_employee(Manager())  # OK


B_co = TypeVar("B_co", covariant=True)


def func(x: list[B_co]) -> B_co:  # OK
    ...


class Co(Generic[T_co]):
    ...


class Contra(Generic[T_contra]):
    ...


class Inv(Generic[T]):
    ...


class CoContra(Generic[T_co, T_contra]):
    ...


class Class1(Inv[T_co]):  # Type error: Inv requires invariant TypeVar
    pass


class Class2(Inv[T_contra]):  # Type error: Inv requires invariant TypeVar
    pass


class Co_Child1(Co[T_co]):  # OK
    ...


class Co_Child2(Co[T]):  # OK
    ...


class Co_Child3(Co[T_contra]):  # Type error: Co requires covariant
    ...


class Contra_Child1(Contra[T_contra]):  # OK
    ...


class Contra_Child2(Contra[T]):  # OK
    ...


class Contra_Child3(Contra[T_co]):  # Type error: Contra requires contravariant
    ...


class Contra_Child4(Contra[Co[T_contra]]):  # OK
    ...


class Contra_Child5(Contra[Co[T_co]]):  # Type error: Contra requires contravariant
    ...


class Contra_Child6(Contra[Co[T]]):  # OK
    ...


class CoContra_Child1(CoContra[T_co, T_contra]):  # OK
    ...


class CoContra_Child2(
    CoContra[T_co, T_co]
):  # Type error: Second type arg must be contravariant
    ...


class CoContra_Child3(
    CoContra[T_contra, T_contra]
):  # Type error: First type arg must be covariant
    ...


class CoContra_Child4(CoContra[T, T]):  # OK
    ...


class CoContra_Child5(
    CoContra[Co[T_co], Co[T_co]]
):  # Type error: Second type arg must be contravariant
    ...


class CoToContra(Contra[Co[T_contra]]):  # OK
    ...


class ContraToContra(Contra[Contra[T_co]]):  # OK
    ...


class CoToCo(Co[Co[T_co]]):  # OK
    ...


class ContraToCo(Co[Contra[T_contra]]):  # OK
    ...


class CoToContraToContra(Contra[Co[Contra[T_contra]]]):  # Type error
    ...


class ContraToContraToContra(Contra[Contra[Contra[T_co]]]):  # Type error
    ...


Co_TA = Co[T_co]
Contra_TA = Contra[T_contra]


class CoToContra_WithTA(Contra_TA[Co_TA[T_contra]]):  # OK
    ...


class ContraToContra_WithTA(Contra_TA[Contra_TA[T_co]]):  # OK
    ...


class CoToCo_WithTA(Co_TA[Co_TA[T_co]]):  # OK
    ...


class ContraToCo_WithTA(Co_TA[Contra_TA[T_contra]]):  # OK
    ...


class CoToContraToContra_WithTA(Contra_TA[Co_TA[Contra_TA[T_contra]]]):  # Type error
    ...


class ContraToContraToContra_WithTA(
    Contra_TA[Contra_TA[Contra_TA[T_co]]]
):  # Type error
    ...
