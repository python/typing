"""
Tests the "type" statement introduced in Python 3.12.
"""

from typing import Callable, TypeVar


type GoodAlias1 = int
type GoodAlias2[S1, *S2, **S3] = Callable[S3, S1] | tuple[*S2]
type GoodAlias3 = GoodAlias2[int, tuple[int, str], ...]


class ClassA:
    type GoodAlias4 = int | None


GoodAlias1.bit_count  # Type error: cannot access attribute

GoodAlias1()  # Type error: cannot call alias

print(GoodAlias1.__value__)  # OK
print(GoodAlias1.__type_params__)  # OK
print(GoodAlias1.other_attrib)  # Type error: unknown attribute


class DerivedInt(GoodAlias1):  # Type error: cannot use alias as base class
    pass


def func2(x: object):
    if isinstance(x, GoodAlias1):  # Type error: cannot use alias in isinstance
        pass

var1 = 1

# The following should not be allowed as type aliases.
type BadTypeAlias1 = eval("".join(map(chr, [105, 110, 116])))
type BadTypeAlias2 = [int, str]
type BadTypeAlias3 = ((int, str),)
type BadTypeAlias4 = [int for i in range(1)]
type BadTypeAlias5 = {"a": "b"}
type BadTypeAlias6 = (lambda: int)()
type BadTypeAlias7 = [int][0]
type BadTypeAlias8 = int if 1 < 3 else str
type BadTypeAlias9 = var1
type BadTypeAlias10 = True
type BadTypeAlias11 = 1
type BadTypeAlias12 = list or set
type BadTypeAlias13 = f"{'int'}"

if 1 < 2:
    type BadTypeAlias14 = int  # Type error: redeclared
else:
    type BadTypeAlias14 = int


def func3():
    type BadTypeAlias15 = int  # Type error alias not allowed in function



V = TypeVar("V")

type TA1[K] = dict[K, V] # Type error: combines old and new TypeVars


T1 = TypeVar("T1")

type TA2 = list[T1] # Type error: uses old TypeVar


type RecursiveTypeAlias1[T] = T | list[RecursiveTypeAlias1[T]]

r1_1: RecursiveTypeAlias1[int] = 1
r1_2: RecursiveTypeAlias1[int] = [1, [1, 2, 3]]

type RecursiveTypeAlias2[S: int, T: str, **P] = Callable[P, T] | list[S] | list[RecursiveTypeAlias2[S, T, P]]

r2_1: RecursiveTypeAlias2[str, str, ...] # Type error: not compatible with S bound
r2_2: RecursiveTypeAlias2[int, str, ...]
r2_3: RecursiveTypeAlias2[int, int, ...] # Type error: not compatible with T bound
r2_4: RecursiveTypeAlias2[int, str, [int, str]]

type RecursiveTypeAlias3 = RecursiveTypeAlias3 # Type error: circular definition

type RecursiveTypeAlias4[T] = T | RecursiveTypeAlias4[str] # Type error: circular definition

type RecursiveTypeAlias5[T] = T | list[RecursiveTypeAlias5[T]]

type RecursiveTypeAlias6 = RecursiveTypeAlias7 # Type error: circular definition
type RecursiveTypeAlias7 = RecursiveTypeAlias6

