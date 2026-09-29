"""
Tests the evaluation of metaclass constructor calls (calls to a metaclass
that create a new class).
"""

from typing import Any, Never, assert_type

# Specification: https://typing.readthedocs.io/en/latest/spec/constructors.html#metaclass-constructors

# > In both cases, the metaclass call should be evaluated using the same rules
# > described in the sections above: the __call__() method of the metaclass's
# > own metaclass (typically type.__call__()) is invoked, which in turn calls
# > the __new__() and __init__() methods of the metaclass.


class MetaMeta(type):
    def __call__(cls, *args, **kwargs) -> Never:
        raise TypeError("Classes cannot be created with this metaclass")


class Meta1(type, metaclass=MetaMeta):
    pass


# This needs to be in a separate scope, because some type checkers might mark
# the statements after it as unreachable.
if bool():
    assert_type(Meta1("A", (), {}), Never)


class Meta2(type):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        key: int,
    ):
        return super().__new__(mcls, name, bases, namespace)


# The return type is an instance of the metaclass being called, but type
# checkers may infer a more precise type, so assignability is checked
# instead of using assert_type().
meta2_instance: Meta2 = Meta2("B", (), {}, key=1)  # OK
Meta2("B", (), {})  # E: missing keyword argument "key"
Meta2("B", (), {}, key="")  # E: wrong type for "key"


# > If the evaluated return type of __new__() is not the class being
# > constructed (or a subclass thereof), a type checker should assume that the
# > __init__() method will not be called.


class Meta3(type):
    def __new__(
        mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> int:
        return 0

    # Not evaluated, as __new__() does not return an instance of Meta3:
    def __init__(cls, x: str) -> None:
        pass


assert_type(Meta3("C", (), {}), int)
