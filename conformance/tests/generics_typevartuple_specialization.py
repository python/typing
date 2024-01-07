"""
Tests the handling of a TypeVarTuple specialization.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/generics.html#behaviour-when-type-parameters-are-not-specified

from typing import Any, Generic, NewType, TypeVar, TypeVarTuple, assert_type


Ts = TypeVarTuple("Ts")
Height = NewType("Height", int)
Width = NewType("Width", int)
Time = NewType("Time", int)


class Array(Generic[*Ts]):
    ...


def takes_any_array1(arr: Array):
    ...


def takes_any_array2(arr: Array[*tuple[Any, ...]]):
    ...


def func1(x: Array[Height, Width]):
    takes_any_array1(x)  # OK
    takes_any_array2(x)  # OK


def func2(y: Array[Time, Height, Width]):
    takes_any_array1(y)  # OK
    takes_any_array2(y)  # OK


# > Generic aliases can be created using a type variable tuple in a similar
# > way to regular type variables.

IntTuple = tuple[int, *Ts]
NamedArray = tuple[str, Array[*Ts]]


def func3(a: IntTuple[float, bool], b: NamedArray[Height]):
    assert_type(a, tuple[int, float, bool])
    assert_type(b, tuple[str, Array[Height]])


def func4(a: IntTuple[()], b: NamedArray[()]):
    assert_type(a, tuple[int])
    assert_type(b, tuple[str, Array[()]])


Shape = TypeVarTuple("Shape")
DType = TypeVar("DType")


class Array2(Generic[DType, *Shape]):
    ...


FloatArray = Array2[float, *Shape]
Array1D = Array2[DType, Any]


def func5(a: Array1D, b: Array1D[int]):
    assert_type(a, Array2[Any, Any])
    assert_type(b, Array2[int, Any])


def takes_float_array_of_any_shape(x: FloatArray):
    ...


x: FloatArray[Height, Width] = Array2()
takes_float_array_of_any_shape(x)  # OK


def takes_float_array_with_specific_shape(y: FloatArray[Height, Width]):
    ...


y: FloatArray = Array2()
takes_float_array_with_specific_shape(y)  # OK


T = TypeVar("T")
VariadicTuple = tuple[T, *Ts]


def func6(a: VariadicTuple[str, int], b: VariadicTuple[float], c: VariadicTuple):
    assert_type(a, tuple[str, int])
    assert_type(b, tuple[float])
    assert_type(c, tuple[Any, ...])


Ts1 = TypeVarTuple("Ts1")
Ts2 = TypeVarTuple("Ts2")

IntTupleVar = tuple[int, *Ts1]  # OK
IntFloatTupleVar = IntTupleVar[float, *Ts2]  # OK
IntFloatsTupleVar = IntTupleVar[*tuple[float, ...]]  # OK


IntTupleGeneric = tuple[int, T]

IntTupleGeneric[str]  # OK
IntTupleGeneric[*Ts]  # Type error
IntTupleGeneric[*tuple[float, ...]]  # Type error


T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")

TA1 = tuple[*Ts, T1, T2]  # OK
TA2 = tuple[T1, T2, *Ts]  # OK
TA3 = tuple[T1, *Ts, T2, T3]  # OK
TA4 = tuple[T1, T2, *tuple[int, ...]]  # OK
TA5 = tuple[T1, *Ts, T2, *Ts]  # Type error
TA6 = tuple[T1, *Ts, T2, *tuple[int, ...]]  # Type error


TA7 = tuple[*Ts, T1, T2]

v1: TA7[int]  # Type error: requires at least two type arguments


def func7(a: TA7[*Ts, T1, T2]) -> tuple[tuple[*Ts], T1, T2]:
    ...


def func8(a: TA7[str, bool], b: TA7[str, bool, float], c: TA7[str, bool, float, int]):
    assert_type(func7(a), tuple[tuple[()], str, bool])
    assert_type(func7(b), tuple[tuple[str], bool, float])
    assert_type(func7(c), tuple[tuple[str, bool], float, int])


TA8 = tuple[T1, *Ts, T2, T3]


def func9(a: TA8[T1, *Ts, T2, T3]) -> tuple[tuple[*Ts], T1, T2, T3]:
    ...


def func10(a: TA8[str, bool, float], b: TA8[str, bool, float, int]):
    assert_type(func9(a), tuple[tuple[()], str, bool, float])
    assert_type(func9(b), tuple[tuple[bool], str, float, int])


TA9 = tuple[*Ts, T1]
TA10 = TA9[*tuple[int, ...]]  # OK


def func11(a: TA10, b: TA9[*tuple[int, ...], str], c: TA9[str, *tuple[int, ...]]):
    assert_type(a, tuple[*tuple[int, ...], int])
    assert_type(b, tuple[*tuple[int, ...], str])
    assert_type(c, tuple[str, *tuple[int, ...], int])


TA11 = tuple[T, *Ts1]
v2: TA11[*Ts2]  # Type error
