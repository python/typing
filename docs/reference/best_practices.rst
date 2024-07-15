.. _best-practices:

*********************
Typing Best Practices
*********************

Introduction
============

Over time, some best practices have proven themselves as useful when working
with type hints in Python. Not all practices are applicable in all situations
and some practices come down to personal style and preference, but they
are a good default set of recommendations to fall back to, unless there is
a specific reason to deviate.

These best practices are constantly evolving, especially as the typing
capabilities and ecosystem grow. So expect new best practices to be added
and existing best practices to be modified or even removed as better practices
evolve. That is why we would love to hear from your experiences with typing.
Please see :ref:`contact` on how to join the discussion.

Typing Features
===============

Type Aliases
------------

Use ``TypeAlias`` for type aliases (but not for regular aliases).

Yes::

    _IntList: TypeAlias = list[int]
    g = os.stat
    Path = pathlib.Path
    ERROR = errno.EEXIST

No::

    _IntList = list[int]
    g: TypeAlias = os.stat
    Path: TypeAlias = pathlib.Path
    ERROR: TypeAlias = errno.EEXIST

Ergonomic Practices
===================

Using ``Any`` and ``object``
----------------------------

Generally, use ``Any`` when a type cannot be expressed appropriately
with the current type system or using the correct type is unergonomic.

If a function accepts every possible object as an argument, for example
because it's only passed to ``str()``, use ``object`` instead of ``Any`` as
type annotation. Similarly, if the return value of a callback is ignored,
annotate it with ``object``::

    def call_cb_if_int(cb: Callable[[int], object], o: object) -> None:
        if isinstance(o, int):
            cb(o)

Arguments and Return Types
--------------------------

For arguments, prefer protocols and abstract types (``Mapping``,
``Sequence``, ``Iterable``, etc.). If an argument accepts literally any value,
use ``object`` instead of ``Any``.

For return values, prefer concrete types (``list``, ``dict``, etc.) for
concrete implementations. The return values of protocols
and abstract base classes must be judged on a case-by-case basis.

Yes::

    def map_it(input: Iterable[str]) -> list[int]: ...
    def create_map() -> dict[str, int]: ...
    def to_string(o: object) -> str: ...  # accepts any object

No::

    def map_it(input: list[str]) -> list[int]: ...
    def create_map() -> MutableMapping[str, int]: ...
    def to_string(o: Any) -> str: ...

Maybe::

    class MyProto(Protocol):
        def foo(self) -> list[int]: ...
        def bar(self) -> Mapping[str, str]: ...

Avoid union return types, since they require ``isinstance()`` checks.
Use ``Any`` or ``X | Any`` if necessary.

Stylistic Practices
===================

Shorthand Syntax
----------------

Where possible, use shorthand syntax for unions instead of
``Union`` or ``Optional``. ``None`` should be the last
element of an union.

Yes::

    def foo(x: str | int) -> None: ...
    def bar(x: str | None) -> int | None: ...

No::

    def foo(x: Union[str, int]) -> None: ...
    def bar(x: Optional[str]) -> Optional[int]: ...
    def baz(x: None | str) -> None: ...

Types
-----

Use ``float`` instead of ``int | float``.
Use ``None`` instead of ``Literal[None]``.

Built-in Generics
-----------------

Use built-in generics instead of the aliases from ``typing``,
where possible.

Yes::

    from collections.abc import Iterable

    def foo(x: type[MyClass]) -> list[str]: ...
    def bar(x: Iterable[str]) -> None: ...

No::

    from typing import Iterable, List, Type

    def foo(x: Type[MyClass]) -> List[str]: ...
    def bar(x: Iterable[str]) -> None: ...
