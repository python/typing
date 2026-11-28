"""
Tests the use of an unpacked TypedDict for annotating **kwargs.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/callables.html#unpack-for-keyword-arguments

# This sample tests the handling of Unpack[TypedDict] when used with
# a **kwargs parameter in a function signature.

from typing import Protocol, TypeVar, Never, NotRequired, Required, Unpack, assert_type
from typing_extensions import TypedDict  # for the `closed` and `extra_items` arguments


class TD1(TypedDict):
    v1: Required[int]
    v2: NotRequired[str]


class TD2(TD1):
    v3: Required[str]


class TD3(TD1, closed=True):
    v3: Required[str]


class TD4(TD1, extra_items=Never):
    v3: Required[str]


def func1(**kwargs: Unpack[TD2]) -> None:
    v1 = kwargs["v1"]
    assert_type(v1, int)

    # > Type checkers may allow reading an item using ``d['x']`` even if
    # > the key ``'x'`` is not required
    kwargs["v2"]  # E?: v2 may not be present

    if "v2" in kwargs:
        v2 = kwargs["v2"]
        assert_type(v2, str)

    v3 = kwargs["v3"]
    assert_type(v3, str)


def func2(v3: str, **kwargs: Unpack[TD1]) -> None:
    # > When Unpack is used, type checkers treat kwargs inside the function
    # > body as a TypedDict.
    assert_type(kwargs, TD1)


def func3() -> None:
    # Mypy reports multiple errors here.
    func1()  # E: missing required keyword args
    func1(v1=1, v2="", v3="5")  # OK

    td2 = TD2(v1=2, v3="4")
    func1(**td2)  # OK
    func1(v1=1, v2="", v3="5", v4=5)  # E?: v4 is not in TD2, but could be in a  subtype
    func1(1, "", "5")  # E: args not passed by position

    # > Passing a dictionary of type dict[str, object] as a **kwargs argument
    # > to a function that has **kwargs annotated with Unpack must generate a
    # > type checker error.
    my_dict: dict[str, str] = {}
    func1(**my_dict)  # E: untyped dict

    d1 = {"v1": 2, "v3": "4", "v4": 4}
    func1(**d1)  # E?: OK or Type error (spec allows either)
    func2(**td2)  # OK
    func1(v1=2, **td2)  # E: v1 is already specified
    func2(1, **td2)  # E: v1 is already specified
    func2(v1=1, **td2)  # E: v1 is already specified


class TDProtocol1(Protocol):
    def __call__(self, *, v1: int, v3: str) -> None:
        ...


class TDProtocol2(Protocol):
    def __call__(self, *, v1: int, v3: str, v2: str = "") -> None:
        ...


class TDProtocol3(Protocol):
    def __call__(self, *, v1: int, v2: int, v3: str) -> None:
        ...


class TDProtocol4(Protocol):
    def __call__(self, *, v1: int) -> None:
        ...


class TDProtocol5(Protocol):
    def __call__(self, v1: int, v3: str) -> None:
        ...


class TDProtocol6(Protocol):
    def __call__(self, **kwargs: Unpack[TD2]) -> None:
        ...


class TDProtocol7(Protocol):
    def __call__(self, **kwargs: Unpack[TD3]) -> None:
        ...


class TDProtocol8(Protocol):
    def __call__(self, **kwargs: Unpack[TD4]) -> None:
        ...


# Specification: https://typing.readthedocs.io/en/latest/spec/callables.html#unpack-kwargs-assignability

v1: TDProtocol1 = func1  # OK
v2: TDProtocol2 = func1  # OK
v3: TDProtocol3 = func1  # E: v2 is wrong type
v4: TDProtocol4 = func1  # E: v3 is missing
v5: TDProtocol5 = func1  # E: params are positional
v6: TDProtocol6 = func1  # OK


def func4(v1: int, /, **kwargs: Unpack[TD2]) -> None:
    ...


def func5(v1: int, **kwargs: Unpack[TD2]) -> None:  # E: parameter v1 overlaps with the TypedDict.
    ...


T = TypeVar("T", bound=TD2)

# > TypedDict is the only permitted heterogeneous type for typing **kwargs.
# > Therefore, in the context of typing **kwargs, using Unpack with types other
# > than TypedDict should not be allowed and type checkers should generate
# > errors in such cases.

def func6(**kwargs: Unpack[T]) -> None:  # E: unpacked value must be a TypedDict, not a TypeVar bound to TypedDict.
    ...


def func7(*, v1: int, v3: str, v2: str = "") -> None:
    ...


v7: TDProtocol6 = func7  # E: source does not have kwargs
v8: TDProtocol7 = func7  # OK, unpacked TypedDict has closed=True
v9: TDProtocol8 = func7  # OK, unpacked TypedDict has extra_items=Never


# An override without **kwargs is not compatible with a base method
# whose **kwargs is an unpacked open TypedDict.


class TDPerson(TypedDict):
    name: str
    age: int


class BaseUnpacked:
    def method(self, **kwargs: Unpack[TDPerson]) -> None:
        ...


class SubNoKwargs(BaseUnpacked):
    def method(self, *, name: str, age: int, extra: bool = False) -> None:  # E: source does not have kwargs
        ...


# An open TypedDict used to annotate **kwargs is treated as having extra items
# of type `object`, so a callable that accepts additional non-required keys
# cannot be assigned to one that only accepts the base TypedDict's keys.


class TDBase(TypedDict):
    x: int


class TDChild(TDBase, total=False):
    y: int


class TDProtocol9(Protocol):
    def __call__(self, **kwargs: Unpack[TDBase]) -> None:
        ...


class TDProtocol10(Protocol):
    def __call__(self, **kwargs: Unpack[TDChild]) -> None:
        ...


def func8(**kwargs: Unpack[TDBase]) -> None:
    ...


def func9(**kwargs: Unpack[TDChild]) -> None:
    ...


v10: TDProtocol9 = func9  # E: `y` may be passed as an extra item of type `object`
v11: TDProtocol10 = func8  # OK


# Specification: https://typing.readthedocs.io/en/latest/spec/callables.html#unpacking-a-typeddict-as-keyword-argument-types


class TDOpenImplicit(TypedDict):
    name: str


class TDOpenExplicit(TypedDict, closed=False):
    name: str


class TDClosed(TypedDict, closed=True):
    name: str


class TDExtraItems(TypedDict, extra_items=int):
    name: str


class TDExtraItemsNever(TypedDict, extra_items=Never):
    name: str


class TDExtraItemsObject(TypedDict, extra_items=object):
    name: str


def takes_name(name: str) -> None:
    ...


def takes_name_kwargs(name: str, **kwargs) -> None:
    ...


def takes_name_object_kwargs(name: str, **kwargs: object) -> None:
    ...


def takes_name_str_kwargs(name: str, **kwargs: str) -> None:
    ...


def takes_name_int_kwargs(name: str, **kwargs: int) -> None:
    ...


def takes_optional_label_int_kwargs(name: str, *, label: str = "", **kwargs: int) -> None:
    ...


def takes_closed(**kwargs: Unpack[TDClosed]) -> None:
    ...


# Equivalent to `def takes_extra_items_object(*, name: str, **kwargs: object)`.
def takes_extra_items_object(**kwargs: Unpack[TDExtraItemsObject]) -> None:
    ...


# Equivalent to `def takes_extra_items_int(*, name: str, **kwargs: int)`.
def takes_extra_items_int(**kwargs: Unpack[TDExtraItems]) -> None:
    ...


# > Type checkers should treat the :term:`extra items` of an unpacked ``TypedDict`` (of type ``object`` if it is :term:`open`) as additional keyword arguments of that
# > type, and report an error unless the callee accepts them: the extra items type must be assignable to the callee's ``**kwargs`` type, and to any keyword parameter [...]

def open_implicit(value: TDOpenImplicit, **kwargs: Unpack[TDOpenImplicit]) -> None:
    takes_name(**value)  # E: a subtype may contain unknown keys
    takes_name_kwargs(**value)
    takes_name_str_kwargs(**value) # E: extra items type is not compatible
    takes_name(**kwargs)  # E: a subtype may contain unknown keys
    takes_name_kwargs(**kwargs)
    takes_name_str_kwargs(**kwargs) # E: extra items type is not compatible
    takes_closed(**value)  # E: a subtype may contain unknown keys
    takes_closed(**kwargs)  # E: a subtype may contain unknown keys
    takes_name_object_kwargs(**value)
    takes_name_object_kwargs(**kwargs)
    takes_extra_items_object(**value)
    takes_extra_items_object(**kwargs)
    takes_extra_items_int(**value)  # E: extra items type is not compatible
    takes_extra_items_int(**kwargs)  # E: extra items type is not compatible


def open_explicit(value:TDOpenExplicit, **kwargs: Unpack[TDOpenExplicit]) -> None:
    takes_name(**value)  # E: a subtype may contain unknown keys
    takes_name_kwargs(**value)
    takes_name_str_kwargs(**value) # E: extra items type is not compatible
    takes_name(**kwargs)  # E: a subtype may contain unknown keys
    takes_name_kwargs(**kwargs)
    takes_name_str_kwargs(**kwargs) # E: extra items type is not compatible
    takes_closed(**value)  # E: a subtype may contain unknown keys
    takes_closed(**kwargs)  # E: a subtype may contain unknown keys
    takes_name_object_kwargs(**value)
    takes_name_object_kwargs(**kwargs)
    takes_extra_items_object(**value)
    takes_extra_items_object(**kwargs)
    takes_extra_items_int(**value)  # E: extra items type is not compatible
    takes_extra_items_int(**kwargs)  # E: extra items type is not compatible


def kwargs_closed(value: TDClosed, **kwargs: Unpack[TDClosed]) -> None:
    takes_name(**value)
    takes_name_kwargs(**value)
    takes_name_str_kwargs(**value)
    takes_name(**kwargs)
    takes_name_kwargs(**kwargs)
    takes_name_str_kwargs(**kwargs)
    takes_closed(**value)
    takes_closed(**kwargs)


def kwargs_extra_items(value: TDExtraItems, **kwargs: Unpack[TDExtraItems]) -> None:
    takes_name(**value)  # E: extra items may be present
    takes_name_str_kwargs(**value)  # E: extra items type is not compatible
    takes_name_int_kwargs(**value)
    takes_name(**kwargs)  # E: extra items may be present
    takes_name_str_kwargs(**kwargs)  # E: extra items type is not compatible
    takes_name_int_kwargs(**kwargs)
    takes_closed(**value) # E: extra items may be present
    takes_closed(**kwargs) # E: extra items may be present
    takes_optional_label_int_kwargs(**value)  # E: extra items type is not compatible w/ `label` param
    takes_optional_label_int_kwargs(**kwargs)  # E: extra items type is not compatible w/ `label` param
    takes_extra_items_object(**value)
    takes_extra_items_object(**kwargs)
    takes_extra_items_int(**value)
    takes_extra_items_int(**kwargs)


def kwargs_extra_items_never(value: TDExtraItemsNever, **kwargs: Unpack[TDExtraItemsNever]) -> None:
    takes_name(**value)
    takes_name_kwargs(**value)
    takes_name_str_kwargs(**value)
    takes_name(**kwargs)
    takes_name_kwargs(**kwargs)
    takes_name_str_kwargs(**kwargs)
    takes_closed(**value)
    takes_closed(**kwargs)
