.. _stubs:

**********
Type Stubs
**********

Supported Constructs
====================

Comments
--------

Standard Python comments are accepted everywhere Python syntax allows them.

Two kinds of structured comments are accepted:

* A ``# type: X`` comment at the end of a line that defines a variable,
  declaring that the variable has type ``X``. However, :pep:`526`-style
  variable annotations are preferred over type comments.
* A ``# type: ignore`` comment at the end of any line, which suppresses all type
  errors in that line. The type checker mypy supports suppressing certain
  type errors by using ``# type: ignore[error-type]``. This is not supported
  by other type checkers and should not be used in stubs.

Imports
-------

Type stubs distinguish between imports that are re-exported and those
that are only used internally. Imports are re-exported if they use one of these
forms (:pep:`484`):

* ``import X as X``
* ``from Y import X as X``
* ``from Y import *``

Here are some examples of imports that make names available for internal use in
a stub but do not re-export them::

    import X
    from Y import X
    from Y import X as OtherX

Type aliases can be used to re-export an import under a different name::

    from foo import bar as _bar
    new_bar = _bar  # "bar" gets re-exported with the name "new_bar"

Sub-modules are always exported when they are imported in a module.
For example, consider the following file structure::

    foo/
        __init__.pyi
        bar.pyi

Then ``foo`` will export ``bar`` when one of the following constructs is used in
``__init__.pyi``::

    from . import bar
    from .bar import Bar

Stubs support customizing star import semantics by defining a module-level
variable called ``__all__``. In stubs, this must be a string list literal.
Other types are not supported. Neither is the dynamic creation of this
variable (for example by concatenation).

By default, ``from foo import *`` imports all names in ``foo`` that
do not begin with an underscore. When ``__all__`` is defined, only those names
specified in ``__all__`` are imported::

    __all__ = ['public_attr', '_private_looking_public_attr']

    public_attr: int
    _private_looking_public_attr: int
    private_attr: int

Type checkers support cyclic imports in stub files.

Built-in Generics
-----------------

:pep:`585` built-in generics are supported and should be used instead
of the corresponding types from ``typing``::

    from collections import defaultdict

    def foo(t: type[MyClass]) -> list[int]: ...
    x: defaultdict[int]

Using imports from ``collections.abc`` instead of ``typing`` is
generally possible and recommended::

    from collections.abc import Iterable

    def foo(iter: Iterable[int]) -> None: ...

Unions
------

Declaring unions with the shorthand syntax or ``Union`` and ``Optional`` is
supported by all type checkers::

    def foo(x: int | str) -> int | None: ...  # recommended
    def foo(x: Union[int, str]) -> Optional[int]: ...  # ok

Module Level Attributes
-----------------------

Module level variables and constants can be annotated using either
type comments or variable annotation syntax::

    x: int  # recommended
    x: int = 0
    x = 0  # type: int
    x = ...  # type: int

The type of a variable is unspecified when the variable is unannotated or
when the annotation
and the assigned value disagree. As an exception, the ellipsis literal can
stand in for any type::

    x = 0  # type is unspecified
    x = ...  # type is unspecified
    x: int = ""  # type is unspecified
    x: int = ...  # type is int

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

Aliases and NewType
-------------------

Type checkers should accept module-level type aliases, optionally using
``TypeAlias`` (:pep:`613`), e.g.::

  _IntList = list[int]
  _StrList: TypeAlias = list[str]

Type checkers should also accept regular module-level or class-level aliases,
e.g.::

  def a() -> None: ...
  b = a

  class C:
      def f(self) -> int: ...
      g = f

A type alias may contain type variables. As per :pep:`484`,
all type variables must be substituted when the alias is used::

  _K = TypeVar("_K")
  _V = TypeVar("_V")
  _MyMap: TypeAlias = dict[str, dict[_K, _V]]

  # either concrete types or other type variables can be substituted
  def f(x: _MyMap[str, _V]) -> _V: ...
  # explicitly substitute in Any rather than using a bare alias
  def g(x: _MyMap[Any, Any]) -> Any: ...

Otherwise, type variables in aliases follow the same rules as type variables in
generic class definitions.

``typing.NewType`` is also supported in stubs.

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

Version and Platform Checks
---------------------------

Type stubs for libraries that support multiple Python versions can use version
checks to supply version-specific type hints. Type stubs for different Python
versions should still conform to the most recent supported Python version's
syntax, as explain in the Syntax_ section above.

Version checks are if-statements that use ``sys.version_info`` to determine the
current Python version. Version checks should only check against the ``major`` and
``minor`` parts of ``sys.version_info``. Type checkers are only required to
support the tuple-based version check syntax::

    if sys.version_info >= (3,):
        # Python 3-specific type hints. This tuple-based syntax is recommended.
    else:
        # Python 2-specific type hints.

    if sys.version_info >= (3, 5):
        # Specific minor version features can be easily checked with tuples.

    if sys.version_info < (3,):
        # This is only necessary when a feature has no Python 3 equivalent.

Type stubs should avoid checking against ``sys.version_info.major``
directly and should not use comparison operators other than ``<`` and ``>=``.

No::

    if sys.version_info.major >= 3:
        # Semantically the same as the first tuple check.

    if sys.version_info[0] >= 3:
        # This is also the same.

    if sys.version_info <= (2, 7):
        # This does not work because e.g. (2, 7, 1) > (2, 7).

Some type stubs also may need to specify type hints for different platforms.
Platform checks must be equality comparisons between ``sys.platform`` and the name
of a platform as a string literal:

Yes::

    if sys.platform == 'win32':
        # Windows-specific type hints.
    else:
        # Posix-specific type hints.

No::

    if sys.platform.startswith('linux'):
        # Not necessary since Python 3.3.

    if sys.platform in ['linux', 'cygwin', 'darwin']:
        # Only '==' or '!=' should be used in platform checks.

Version and platform comparisons can be chained using the ``and`` and ``or``
operators::

    if sys.platform == 'linux' and (sys.version_info < (3,) or sys,version_info >= (3, 7)): ...

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
