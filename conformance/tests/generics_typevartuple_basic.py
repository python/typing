"""
Tests basic usage of TypeVarTuple.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/generics.html#typevartuple

from typing import Generic, NewType, TypeVarTuple, assert_type

Ts = TypeVarTuple("Ts")


class Array1(Generic[*Ts]):
    ...


def func1(*args: *Ts) -> tuple[*Ts]:
    ...


Shape = TypeVarTuple("Shape")


class Array(Generic[*Shape]):
    def __init__(self, shape: tuple[*Shape]):
        self._shape: tuple[*Shape] = shape

    def get_shape(self) -> tuple[*Shape]:
        return self._shape


Height = NewType("Height", int)
Width = NewType("Width", int)
Time = NewType("Time", int)
Batch = NewType("Batch", int)

v1: Array[Height, Width] = Array((Height(1), Width(2)))  # OK
v2: Array[Batch, Height, Width] = Array((Batch(1), Height(1), Width(1)))  # OK
v3: Array[Time, Batch, Height, Width] = Array(
    (Time(1), Batch(1), Height(1), Width(1))
)  # OK

v4: Array[Height, Width] = Array(Height(1))  # Type error
v5: Array[Batch, Height, Width] = Array((Batch(1), Width(1)))  # Type error
v6: Array[Time, Batch, Height, Width] = Array(
    (Time(1), Batch(1), Width(1), Height(1))
)  # Type error


# > Type Variable Tuples Must Always be Unpacked


class ClassA(Generic[Shape]):  # Type error: not unpacked
    def __init__(self, shape: tuple[Shape]):  # Type error: not unpacked
        self._shape: tuple[*Shape] = shape

    def get_shape(self) -> tuple[Shape]:  # Type error: not unpacked
        return self._shape

    def method1(*args: Shape) -> None:  # Type error: not unpacked
        ...


# > TypeVarTuple does not yet support specification of variance, bounds, constraints.

Ts1 = TypeVarTuple("Ts1", covariant=True)  # Type error
Ts2 = TypeVarTuple("Ts2", int, float)  # Type error
Ts3 = TypeVarTuple("Ts3", bound=int)  # Type error


# > If the same TypeVarTuple instance is used in multiple places in a signature
# > or class, a valid type inference might be to bind the TypeVarTuple to a
# > tuple of a union of types.


def func2(arg1: tuple[*Ts], arg2: tuple[*Ts]) -> tuple[*Ts]:
    ...


# > We do not allow this; type unions may not appear within the tuple.
# > If a type variable tuple appears in multiple places in a signature,
# > the types must match exactly (the list of type parameters must be the
# > same length, and the type parameters themselves must be identical)

# Note from Eric Traut: The above provision in the spec is very problematic
# and will likely need to be changed.

assert_type(func1((0,), (1,)), tuple[int])  # OK
func1((0,), ("0",))  # Type error?
func1((0,), (0.0,))  # Type error?
func1((0.0,), (0,))  # Type error?
func1((0,), (1,))  # Type error?
func1((0, 0), (0,))  # Type error


def multiply(x: Array[*Shape], y: Array[*Shape]) -> Array[*Shape]:
    ...


def func3(x: Array[Height], y: Array[Width], z: Array[Height, Width]):
    multiply(x, x)  # OK
    multiply(x, y)  # Type error
    multiply(x, z)  # Type error


# > Only a single type variable tuple may appear in a type parameter list.


class Array3(Generic[*Ts1, *Ts2]):  # Type error
    ...
