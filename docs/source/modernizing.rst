.. role:: python(code)
   :language: python

.. role:: t-ext(class)

.. _modernizing:

**************************************
Modernizing Superseded Typing Features
**************************************

Introduction
============

This guide helps to modernize your code by replacing older typing features
with their modern equivalents. Not all features described here are obsolete,
but they are superseded by more modern alternatives, that are recommended to use.

These newer features are not available in all Python versions, although
some features are available as backports from the
`typing-extensions <https://pypi.org/project/typing-extensions/>`_
package, or require quoting or using :python:`from __future__ import annotations`.
Each section states the minimum Python version required to use the
feature, whether it is available in typing-extensions, and whether it is
available using quoting.

.. note::

    The latest version of typing-extensions is available for all Python
    versions that have not reached their end of life, but not necessarily for
    older versions.

.. note::

    :python:`from __future__ import annotations` is available since Python 3.7.
    This will only work inside type annotations, while quoting is still
    required outside. For example, this example runs on Python 3.7 and up,
    although the pipe operator was only introduced in Python 3.10::

        from __future__ import annotations
        from typing_extensions import TypeAlias

        def f(x: int | None) -> int | str: ...  # the future import is sufficient
        Alias: TypeAlias = "int | str"  # this requires quoting

.. _modernizing-type-comments:

Type Comments
=============

*Alternative available since:* Python 3.0, 3.6

Type comments were originally introduced to support type annotations in
Python 2 and variable annotations before Python 3.6. While most type checkers
still support them, they are considered obsolete, and type checkers are
not required to support them.

For example, replace::

    x = 3  # type: int
    def f(x, y):  # type: (int, int) -> int
        return x + y

with::

    x: int = 3
    def f(x: int, y: int) -> int:
        return x + y

When using forward references or types only available during type checking,
it's necessary to either use :python:`from __future__ import annotations`
(available since Python 3.7) or to quote the type::

    def f(x: "Parrot") -> int: ...

    class Parrot: ...

.. _modernizing-typing-text:

``typing.Text``
===============

*Alternative available since:* Python 3.0

:class:`typing.Text` was a type alias intended for Python 2 compatibility.
It is equivalent to :class:`str` and should be replaced with it.
For example, replace::

    from typing import Text

    def f(x: Text) -> Text: ...

with::

    def f(x: str) -> str: ...

.. _modernizing-typed-dict:

``typing.TypedDict`` Legacy Forms
=================================

*Alternative available since:* Python 3.6

:class:`TypedDict <typing.TypedDict>` supports two legacy forms for
supporting Python versions that don't support variable annotations.
Replace these two variants::

    from typing import TypedDict

    FlyingSaucer = TypedDict("FlyingSaucer", {"x": int, "y": str})
    FlyingSaucer = TypedDict("FlyingSaucer", x=int, y=str)

with::

    class FlyingSaucer(TypedDict):
        x: int
        y: str

But the dictionary form is still necessary if the keys are not valid Python
identifiers::

    Airspeeds = TypedDict("Airspeeds", {"unladen-swallow": int})

.. _modernizing-generics:

Generics in the ``typing`` Module
=================================

*Alternative available since:* Python 3.0 (quoted), Python 3.9 (unquoted)

Originally, the :mod:`typing` module provided aliases for built-in types that
accepted type parameters. Since Python 3.9, these aliases are no longer
necessary, and can be replaced with the built-in types. For example,
replace::

    from typing import Dict, List

    def f(x: List[int]) -> Dict[str, int]: ...

with::

    def f(x: list[int]) -> dict[str, int]: ...

This affects the following types:

* :class:`typing.Dict` (→ :class:`dict`)
* :class:`typing.FrozenSet` (→ :class:`frozenset`)
* :class:`typing.List` (→ :class:`list`)
* :class:`typing.Set` (→ :class:`set`)
* :data:`typing.Tuple` (→ :class:`tuple`)

The :mod:`typing` module also provided aliases for certain standard library
types that accepted type parameters. Since Python 3.9, these aliases are no
longer necessary, and can be replaced with the proper types. For example,
replace::

    from typing import DefaultDict, Pattern

    def f(x: Pattern[str]) -> DefaultDict[str, int]: ...

with::

    from collections import defaultdict
    from re import Pattern

    def f(x: Pattern[str]) -> defaultdict[str, int]: ...

This affects the following types:

* :class:`typing.Deque` (→ :class:`collections.deque`)
* :class:`typing.DefaultDict` (→ :class:`collections.defaultdict`)
* :class:`typing.OrderedDict` (→ :class:`collections.OrderedDict`)
* :class:`typing.Counter` (→ :class:`collections.Counter`)
* :class:`typing.ChainMap` (→ :class:`collections.ChainMap`)
* :class:`typing.Awaitable` (→ :class:`collections.abc.Awaitable`)
* :class:`typing.Coroutine` (→ :class:`collections.abc.Coroutine`)
* :class:`typing.AsyncIterable` (→ :class:`collections.abc.AsyncIterable`)
* :class:`typing.AsyncIterator` (→ :class:`collections.abc.AsyncIterator`)
* :class:`typing.AsyncGenerator` (→ :class:`collections.abc.AsyncGenerator`)
* :class:`typing.Iterable` (→ :class:`collections.abc.Iterable`)
* :class:`typing.Iterator` (→ :class:`collections.abc.Iterator`)
* :class:`typing.Generator` (→ :class:`collections.abc.Generator`)
* :class:`typing.Reversible` (→ :class:`collections.abc.Reversible`)
* :class:`typing.Container` (→ :class:`collections.abc.Container`)
* :class:`typing.Collection` (→ :class:`collections.abc.Collection`)
* :data:`typing.Callable` (→ :class:`collections.abc.Callable`)
* :class:`typing.AbstractSet` (→ :class:`collections.abc.Set`)
* :class:`typing.MutableSet` (→ :class:`collections.abc.MutableSet`)
* :class:`typing.Mapping` (→ :class:`collections.abc.Mapping`)
* :class:`typing.MutableMapping` (→ :class:`collections.abc.MutableMapping`)
* :class:`typing.Sequence` (→ :class:`collections.abc.Sequence`)
* :class:`typing.MutableSequence` (→ :class:`collections.abc.MutableSequence`)
* :class:`typing.ByteString` (→ :class:`collections.abc.ByteString`), but see :ref:`modernizing-byte-string`
* :class:`typing.MappingView` (→ :class:`collections.abc.MappingView`)
* :class:`typing.KeysView` (→ :class:`collections.abc.KeysView`)
* :class:`typing.ItemsView` (→ :class:`collections.abc.ItemsView`)
* :class:`typing.ValuesView` (→ :class:`collections.abc.ValuesView`)
* :class:`typing.ContextManager` (→ :class:`contextlib.AbstractContextManager`)
* :class:`typing.AsyncContextManager` (→ :class:`contextlib.AbstractAsyncContextManager`)
* :class:`typing.Pattern` (→ :class:`re.Pattern`)
* :class:`typing.Match` (→ :class:`re.Match`)

.. _modernizing-union:

``typing.Union`` and ``typing.Optional``
========================================

*Alternative available since:* Python 3.0 (quoted), Python 3.10 (unquoted)

While :data:`Union <typing.Union>` and :data:`Optional <typing.Optional>` are
not considered obsolete, using the ``|`` (pipe) operator is often more
readable. :python:`Union[X, Y]` is equivalent to :python:`X | Y`, while
:python:`Optional[X]` is equivalent to :python:`X | None`.

For example, replace::

    from typing import Optional, Union

    def f(x: Optional[int]) -> Union[int, str]: ...

with::

    def f(x: int | None) -> int | str: ...

.. _modernizing-no-return:

``typing.NoReturn``
===================

*Alternative available since:* Python 3.11, typing-extensions

Python 3.11 introduced :data:`typing.Never` as an alias to
:data:`typing.NoReturn` for use in annotations that are not
return types. For example, replace::

    from typing import NoReturn

    def f(x: int, y: NoReturn) -> None: ...

with::

    from typing import Never  # or typing_extensions.Never

    def f(x: int, y: Never) -> None: ...

But keep ``NoReturn`` for return types::

    from typing import NoReturn

    def f(x: int) -> NoReturn: ...

.. _modernizing-type-aliases:

Type Aliases
============

*Alternative available since:* Python 3.12 (keyword); Python 3.10, typing-extensions

Originally, type aliases were defined using a simple assignment::

    IntList = list[int]

Python 3.12 introduced the :keyword:`type` keyword to define type aliases::

    type IntList = list[int]

Code supporting older Python versions should use
:data:`TypeAlias <typing.TypeAlias>`, introduced in Python 3.10, but also
available in typing-extensions, instead::

    from typing import TypeAlias  # or typing_extensions.TypeAlias

    IntList: TypeAlias = list[int]

.. _modernizing-user-generics:

User Defined Generics
=====================

*Alternative available since:* Python 3.12

Python 3.12 introduced new syntax for defining generic classes. Previously,
generic classes had to derive from :class:`typing.Generic` (or another
generic class) and defined the type variable using :class:`typing.TypeVar`.
For example::

    from typing import Generic, TypeVar

    T = TypeVar("T")

    class Brian(Generic[T]): ...
    class Reg(int, Generic[T]): ...

Starting with Python 3.12, the type variable doesn't need to be declared
using ``TypeVar``, and instead of deriving the class from ``Generic``, the
following syntax can be used::

    class Brian[T]: ...
    class Reg[T](int): ...

.. _modernizing-byte-string:

``typing.ByteString``
=====================

*Alternative available since:* Python 3.0; Python 3.12, typing-extensions

:class:`ByteString <typing.ByteString>` was originally intended to be a type
alias for "byte-like" types, i.e. :class:`bytes`, :class:`bytearray`, and
:class:`memoryview`. In practice, this
is seldom exactly what is needed. Use one of these alternatives instead:

* Just :class:`bytes` is often sufficient, especially when not declaring
  a public API.
* For items that accept any type that supports the
  :ref:`buffer protocol <bufferobjects>`, use :class:`collections.abc.Buffer`
  (available since Python 3.12) or :t-ext:`typing_extensions.Buffer`.
* Otherwise, use a union of :class:`bytes`, :class:`bytearray`,
  :class:`memoryview`, and/or any other types that are accepted.

``typing.Hashable`` and ``typing.Sized``
========================================

*Alternative available since:* Python 3.12, typing-extensions

The following abstract base classes from :mod:`typing` were added to
:mod:`collections.abc` in Python 3.12:

* :class:`typing.Hashable` (→ :class:`collections.abc.Hashable`)
* :class:`typing.Sized` (→ :class:`collections.abc.Sized`)

Update your imports to use the new locations::

    from collections.abc import Hashable, Sized

    def f(x: Hashable) -> Sized: ...
