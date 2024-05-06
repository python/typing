"""
Tests Callable annotation and parameter annotations for "def" statements.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/callables.html#callable

from typing import (
    Any,
    Callable,
    Concatenate,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
    assert_type,
)

T_contra = TypeVar("T_contra", contravariant=True)
P = ParamSpec("P")


def func1(cb: Callable[[int, str], list[str]]) -> None:
    assert_type(cb(1, ""), list[str])

    cb(1)  # E
    cb(1, 2)  # E
    cb(1, "", 1)  # E
    # Mypy reports two errors, one for each kwarg.
    cb(a=1, b="")  # E: bad kwarg 'a'


def func2(cb: Callable[[], dict[str, str]]) -> None:
    assert_type(cb(), dict[str, str])

    cb(1)  # E


# https://typing.readthedocs.io/en/latest/spec/callables.html#meaning-of-in-callable


# > The Callable special form supports the use of ... in place of the list of
# > parameter types. This indicates that the type is consistent with any input
# > signature.
def func3(cb: Callable[..., list[str]]):
    assert_type(cb(), list[str])
    assert_type(cb(""), list[str])
    assert_type(cb(1, ""), list[str])


def func4(*args: int, **kwargs: int) -> None:
    assert_type(args, tuple[int, ...])
    assert_type(kwargs, dict[str, int])


v1: Callable[int]  # E
v2: Callable[int, int]  # E
v3: Callable[[], [int]]  # E
v4: Callable[int, int, int]  # E
v5: Callable[[...], int]  # E


def test_cb1(x: int) -> str:
    return ""


def test_cb2() -> str:
    return ""


cb1: Callable[..., str]
cb1 = test_cb1  # OK
cb1 = test_cb2  # OK

cb2: Callable[[], str] = cb1  # OK

# > A ... can also be used with Concatenate. In this case, the parameters prior
# > to the ... are required to be present in the input signature and be
# > compatible in kind and type, but any additional parameters are permitted.


def test_cb3(a: int, b: int, c: int) -> str:
    return ""


def test_cb4(*, a: int) -> str:
    return ""


cb3: Callable[Concatenate[int, ...], str]
cb3 = test_cb1  # OK
cb3 = test_cb2  # E
cb3 = test_cb3  # OK
cb3 = test_cb4  # E

# > If the input signature in a function definition includes both a *args and
# > **kwargs parameter and both are typed as Any (explicitly or implicitly
# > because it has no annotation), a type checker should treat this as the
# > equivalent of `...`. Any other parameters in the signature are unaffected
# > and are retained as part of the signature.


class Proto1(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> None: ...


class Proto2(Protocol):
    def __call__(self, a: int, /, *args, **kwargs) -> None: ...


class Proto3(Protocol):
    def __call__(self, a: int, *args: Any, **kwargs: Any) -> None: ...


class Proto4(Protocol[P]):
    def __call__(self, a: int, *args: P.args, **kwargs: P.kwargs) -> None: ...


class Proto5(Protocol[T_contra]):
    def __call__(self, *args: T_contra, **kwargs: T_contra) -> None: ...


class Proto6(Protocol):
    def __call__(self, a: int, /, *args: Any, k: str, **kwargs: Any) -> None:
        pass


class Proto7(Protocol):
    def __call__(self, a: float, /, b: int, *, k: str, m: str) -> None:
        pass


def func(p1: Proto1, p2: Proto2, p3: Proto3, p7: Proto7):
    assert_type(p1, Callable[..., None])  # OK
    assert_type(p1, Proto5[Any])  # E
    assert_type(p2, Callable[Concatenate[int, ...], None])  # OK
    assert_type(p3, Callable[..., None])  # E
    assert_type(p3, Proto4[...])  # OK

    f1: Proto6 = p7  # OK


# > The ... syntax can also be used to provide a specialized value for a
# > ParamSpec in a generic class or type alias.


Callback1: TypeAlias = Callable[P, str]
Callback2: TypeAlias = Callable[Concatenate[int, P], str]


def func5(cb1: Callable[[], str], cb2: Callable[[int], str]) -> None:
    f1: Callback1[...] = cb1  # OK
    f2: Callback2[...] = cb1  # E

    f3: Callback1[...] = cb2  # OK
    f4: Callback2[...] = cb2  # OK


# > If ... is used with signature concatenation, the ... portion continues
# > to mean “any conceivable set of parameters that could be compatible”.

CallbackWithInt: TypeAlias = Callable[Concatenate[int, P], str]
CallbackWithStr: TypeAlias = Callable[Concatenate[str, P], str]


def func6(cb: Callable[[int, str], str]) -> None:
    f1: Callable[Concatenate[int, ...], str] = cb  # OK
    f2: Callable[Concatenate[str, ...], str] = cb  # E
    f3: CallbackWithInt[...] = cb  # OK
    f4: CallbackWithStr[...] = cb  # E
