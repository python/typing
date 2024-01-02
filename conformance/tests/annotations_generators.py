"""
Tests for annotating generators.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/annotations.html#annotating-generator-functions-and-coroutines

# The return type of generator functions can be annotated by the generic type
# Generator[yield_type, send_type, return_type] provided by typing.py module.

import asyncio
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Generator,
    Iterable,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    assert_type,
)

T = TypeVar("T")


class A:
    pass


class B:
    def should_continue(self) -> bool:
        return True


class C:
    pass


def generator1() -> Generator[A, B, C]:
    cont = B()
    while cont.should_continue():
        yield A()

    return C()


def generator2() -> Generator[A, B, C]:  # Type error: missing return
    cont = B()
    if cont.should_continue():
        return False  # Type error: incompatible return type

    while cont.should_continue():
        yield 3  # Type error: incompatible yield type


def generator3() -> Generator[A, int, Any]:
    cont = B()
    if cont.should_continue():
        return 3

    while cont.should_continue():
        yield 3  # Incompatible yield type


def generator4() -> Iterable[A]:
    yield A()
    return True


def generator5() -> Iterator[A]:
    yield B()  # Type error: incompatible yield type


def generator6() -> Generator[None, None, None]:
    yield


def generator7() -> Iterator[dict[str, int]]:
    yield {"": 0}  # OK


def generator8() -> int:  # Type error: incompatible return type
    yield None
    return 0


async def generator9() -> int:  # Type error: incompatible return type
    yield None


class IntIterator(Protocol):
    def __next__(self, /) -> int:
        ...


def generator15() -> IntIterator:  # OK
    yield 0


class AsyncIntIterator(Protocol):
    def __anext__(self, /) -> Awaitable[int]:
        ...


async def generator16() -> AsyncIntIterator:  # OK
    yield 0


def generator17() -> Iterator[A]:  # OK
    yield from generator17()


def generator18() -> Iterator[B]:
    yield from generator17()  # Type error: incompatible generator type
    yield from [1]  # Type error: incompatible generator type


def generator19() -> Generator[None, float, None]:  # OK
    x: float = yield


def generator20() -> Generator[None, int, None]:  # OK
    yield from generator19()


def generator21() -> Generator[None, int, None]:
    x: float = yield


def generator22() -> Generator[None, str, None]:
    yield from generator21()  # Type error: incompatible send type


def generator23() -> Iterable[str]:  # OK
    return
    yield ""  # Unreachable


async def generator24() -> AsyncIterable[str]:  # OK
    return
    yield ""  # Unreachable


def generator25(ints1: list[int], ints2: list[int]) -> Generator[int, None, None]:  # OK
    yield from ints1
    yield from ints2


async def get_data() -> list[int]:
    await asyncio.sleep(1)
    return [1, 2, 3]


async def generator26(nums: list[int]) -> AsyncGenerator[str, None]:
    for n in nums:
        await asyncio.sleep(1)
        yield f"The number is {n}"


async def generator27() -> AsyncGenerator[str, None]:
    data = await get_data()
    v1 = generator26(data)
    assert_type(v1, AsyncGenerator[str, None])
    return v1


async def generator28() -> AsyncIterator[str]:
    data = await get_data()
    v1 = generator26(data)
    assert_type(v1, AsyncGenerator[str, None])
    return v1
