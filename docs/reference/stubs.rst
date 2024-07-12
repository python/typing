.. _stubs:

**********
Type Stubs
**********

Supported Constructs
====================

Classes
-------

Class definition syntax follows general Python syntax, but type checkers
are only expected to understand the following constructs in class bodies:

* The ellipsis literal ``...`` is ignored and used for empty
  class bodies. Using ``pass`` in class bodies is undefined.
* Instance attributes follow the same rules as module level attributes
  (see above).
* Method definitions (see below) and properties.
* Method aliases.
* Inner class definitions.

More complex statements don't need to be supported::

    class Simple: ...

    class Complex(Base):
        read_write: int
        @property
        def read_only(self) -> int: ...
        def do_stuff(self, y: str) -> None: ...
        doStuff = do_stuff

The type of generic classes can be narrowed by annotating the ``self``
argument of the ``__init__`` method::

    class Foo(Generic[_T]):
        @overload
        def __init__(self: Foo[str], type: Literal["s"]) -> None: ...
        @overload
        def __init__(self: Foo[int], type: Literal["i"]) -> None: ...
        @overload
        def __init__(self, type: str) -> None: ...

The class must match the class in which it is declared. Using other classes,
including sub or super classes, will not work. In addition, the ``self``
annotation cannot contain type variables.

.. _supported-functions:

Functions and Methods
---------------------

Function and method definition syntax follows general Python syntax.
For backwards compatibility, positional-only parameters can also be marked by
prefixing their name with two underscores (but not suffixing it with two
underscores)::

    # x is positional-only
    # y can be used positionally or as keyword argument
    # z is keyword-only
    def foo(x, /, y, *, z): ...  # recommended
    def foo(__x, y, *, z): ...  # backwards compatible syntax

If an argument or return type is unannotated, per :pep:`484` its
type is assumed to be ``Any``. It is preferred to leave unknown
types unannotated rather than explicitly marking them as ``Any``, as some
type checkers can optionally warn about unannotated arguments.

If an argument has a literal or constant default value, it must match the implementation
and the type of the argument (if specified) must match the default value.
Alternatively, ``...`` can be used in place of any default value::

    # The following arguments all have type Any.
    def unannotated(a, b=42, c=...): ...
    # The following arguments all have type int.
    def annotated(a: int, b: int = 42, c: int = ...): ...
    # The following default values are invalid and the types are unspecified.
    def invalid(a: int = "", b: Foo = Foo()): ...

For a class ``C``, the type of the first argument to a classmethod is
assumed to be ``type[C]``, if unannotated. For other non-static methods,
its type is assumed to be ``C``::

    class Foo:
        def do_things(self): ...  # self has type Foo
        @classmethod
        def create_it(cls): ...  # cls has type Type[Foo]
        @staticmethod
        def utility(x): ...  # x has type Any

But::

    _T = TypeVar("_T")

    class Foo:
        def do_things(self: _T) -> _T: ...  # self has type _T
        @classmethod
        def create_it(cls: _T) -> _T: ...  # cls has type _T

:pep:`612` parameter specification variables (``ParamSpec``)
are supported in argument and return types::

    _P = ParamSpec("_P")
    _R = TypeVar("_R")

    def foo(cb: Callable[_P, _R], *args: _P.args, **kwargs: _P.kwargs) -> _R: ...

However, ``Concatenate`` from PEP 612 is not yet supported; nor is using
a ``ParamSpec`` to parameterize a generic class.

:pep:`647` type guards are supported.

Using a function or method body other than the ellipsis literal is currently
unspecified. Stub authors may experiment with other bodies, but it is up to
individual type checkers how to interpret them::

    def foo(): ...  # compatible
    def bar(): pass  # behavior undefined

All variants of overloaded functions and methods must have an ``@overload``
decorator::

    @overload
    def foo(x: str) -> str: ...
    @overload
    def foo(x: float) -> int: ...

The following (which would be used in the implementation) is wrong in
type stubs::

    @overload
    def foo(x: str) -> str: ...
    @overload
    def foo(x: float) -> int: ...
    def foo(x: str | float) -> Any: ...

Decorators
----------

Type stubs may only use decorators defined in the ``typing`` module, plus a
fixed set of additional ones:

* ``classmethod``
* ``staticmethod``
* ``property`` (including ``.setter``)
* ``abc.abstractmethod``
* ``dataclasses.dataclass``
* ``asyncio.coroutine`` (although ``async`` should be used instead)

The behavior of other decorators should instead be incorporated into the types.
For example, for the following function::

  import contextlib
  @contextlib.contextmanager
  def f():
      yield 42

the stub definition should be::

  from contextlib import AbstractContextManager
  def f() -> AbstractContextManager[int]: ...

Enums
-----

Enum classes are supported in stubs, regardless of the Python version targeted by
the stubs.

Enum members may be specified just like other forms of assignments, for example as
``x: int``, ``x = 0``, or ``x = ...``.  The first syntax is preferred because it
allows type checkers to correctly type the ``.value`` attribute of enum members,
without providing unnecessary information like the runtime value of the enum member.

Additional properties on enum members should be specified with ``@property``, so they
do not get interpreted by type checkers as enum members.

Yes::

    from enum import Enum

    class Color(Enum):
        RED: int
        BLUE: int
        @property
        def rgb_value(self) -> int: ...

    class Color(Enum):
        # discouraged; type checkers will not understand that Color.RED.value is an int
        RED = ...
        BLUE = ...
        @property
        def rgb_value(self) -> int: ...

No::

    from enum import Enum

    class Color(Enum):
        RED: int
        BLUE: int
        rgb_value: int  # no way for type checkers to know that this is not an enum member
