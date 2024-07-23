.. _distributing-type:

Distributing type information
=============================

.. _stub-files:

Stub files
----------

(Originally specified in :pep:`484`.)

*Stub files*, also called *type stubs*, provide type information for untyped
Python packages and modules. Stub files serve multiple purposes:

* They are the only way to add type information to extension modules.
* They can provide type information for packages that do not wish to
  add them inline.
* They can be distributed separately from the implementation.
  This allows stubs to be developed at a different pace or by different
  authors, which is especially useful when adding type annotations to
  existing packages.
* They can act as documentation, succinctly explaining the external
  API of a package, without including the implementation or private
  members.

Stub files that use only the constructs described in :ref:`stub-file-supported-constructs`
below should work with all type checkers that conform to this specification. A
conformant type checker will parse a stub that uses only such constructs without
error and will not interpret any construct in a contradictory manner. However,
type checkers are not required to implement checks for all these constructs and
can elect to ignore unsupported ones. Additionally, type checkers can support
constructs not decribed here, and tool authors are encouraged to experiment with
additional features.

.. _stub-file-syntax:

Syntax
^^^^^^

Stub files are syntactically valid Python files in the earliest Python version
that is not yet end-of-life. They use a ``.pyi`` suffix. The Python syntax used
by stub files is independent from the Python versions supported by the
implementation, and from the Python version the type checker runs under (if
any). Therefore, stub authors should use the latest syntax features available in
the earliest supported version, even if the implementation supports older
versions. Type checker authors are encouraged to support syntax features from
newer versions, although stub authors should not use such features if they wish
to maintain compatibility with all type checkers.

For example, Python 3.7 added the ``async`` keyword (see :pep:`492`).
Stub authors should use it to mark coroutines, even if the implementation
still uses the ``@coroutine`` decorator. On the other hand, stubs should not use
the ``type`` soft keyword from :pep:`695`, introduced in Python 3.12, until
Python 3.11 reaches end-of-life in October 2027.

Stubs are treated as if ``from __future__ import annotations`` is enabled. In
particular, built-in generics, pipe union syntax (``X | Y``), and forward
references can be used.

Type checkers should have a configurable search path for stub files. If a stub
file is found, the type checker should not read the corresponding "real" module.
See :ref:`mro` for more information.

.. _stub-file-supported-constructs:

Supported Constructs
^^^^^^^^^^^^^^^^^^^^

This section lists constructs that type checkers will accept in stub files. Stub
authors can safely use these constructs. If a construct is marked as
"unspecified", type checkers may handle it as they best see fit or report an
error. Linters should usually flag those constructs. Stub authors should avoid
using them to ensure compatibility across type checkers.

The `typeshed feature tracker <https://github.com/python/typeshed/labels/project%3A%20feature%20tracker>`_ tracks features from the ``typing`` module that are
not yet supported by all major type checkers. Unless otherwise noted in this
tracker, stub files support all features from the ``typing`` module of the
latest released Python version. If a stub uses typing features from a later
Python version than what the implementation supports, these features can be
imported from ``typing_extensions`` instead of ``typing``

For example, a stub could use ``Literal``, introduced in Python 3.8,
for a library supporting Python 3.7+::

    from typing_extensions import Literal

    def foo(x: Literal[""]) -> int: ...

Comments
""""""""

Standard Python comments are accepted everywhere Python syntax allows them.

Two kinds of structured comments are accepted:

* A ``# type: X`` comment at the end of a line that defines a variable,
  declaring that the variable has type ``X``. However, :pep:`526`-style
  variable annotations are preferred over type comments.
* An error suppression comment at the end of any line. Common error suppression
  formats are ``# type: ignore``, ``# type: ignore[error-class]``, and
  ``# pyright: ignore[error-class]``. Type checkers may ignore error
  suppressions that they don't support but should not error on them.

Imports
"""""""

Stub files distinguish between imports that are re-exported and those
that are only used internally. See :ref:`import-conventions`.

Type aliases can be used to re-export an import under a different name::

    from foo import bar as _bar
    new_bar = _bar  # "bar" gets re-exported with the name "new_bar"

Stubs support customizing star import semantics by defining a module-level
variable called ``__all__``. In stubs, this must be a string list literal.
Other types are not supported. Neither is the dynamic creation of this
variable (for example by concatenation).

When ``__all__`` is defined, exactly those names specified in ``__all__`` are
imported::

    __all__ = ['public_attr', '_private_looking_public_attr']

    public_attr: int
    _private_looking_public_attr: int
    private_attr: int

Type checkers support cyclic imports in stub files.

Built-in Generics
"""""""""""""""""

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
""""""

Declaring unions with the shorthand syntax or ``Union`` and ``Optional`` is
supported by all type checkers::

    def foo(x: int | str) -> int | None: ...  # recommended
    def foo(x: Union[int, str]) -> Optional[int]: ...  # ok

Module Level Attributes
"""""""""""""""""""""""

Module level variables and constants can be annotated using either
type comments or variable annotation syntax::

    x: int  # recommended
    x: int = 0
    x = 0  # type: int
    x = ...  # type: int

The ellipsis literal can stand in for any value::

    x: int = ...  # type is int

A variable annotated as ``Final`` and assigned a literal value has the
corresponding ``Literal`` type::

    x: Final = 0  # type is Literal[0]

In all other cases, the type of a variable is unspecified when the variable is
unannotated or when the annotation and the assigned value disagree::

    x = 0  # type is unspecified
    x = ...  # type is unspecified
    x: int = ""  # type is unspecified

Classes
"""""""

Class definition syntax follows general Python syntax, but type checkers
are expected to understand only the following constructs in class bodies:

* The ellipsis literal ``...`` is ignored and used for empty
  class bodies. Using ``pass`` in class bodies is undefined.
* Instance attributes follow the same rules as module level attributes
  (see above).
* Method definitions (see below) and properties.
* Method aliases.
* Inner class definitions.

Yes::

    class Simple: ...

    class Complex(Base):
        read_write: int
        @property
        def read_only(self) -> int: ...
        def do_stuff(self, y: str) -> None: ...
        doStuff = do_stuff
        class Inner: ...

More complex statements don't need to be supported.

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

Functions and Methods
"""""""""""""""""""""

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
        def create_it(cls): ...  # cls has type type[Foo]
        @staticmethod
        def utility(x): ...  # x has type Any

But::

    _T = TypeVar("_T")

    class Foo:
        def do_things(self: _T) -> _T: ...  # self has type _T
        @classmethod
        def create_it(cls: _T) -> _T: ...  # cls has type _T

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

The following (which would be used in the implementation) is wrong in stubs::

    @overload
    def foo(x: str) -> str: ...
    @overload
    def foo(x: float) -> int: ...
    def foo(x: str | float) -> Any: ...

Aliases and NewType
"""""""""""""""""""

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
""""""""""

Type checkers are expected to understand the effects of all decorators defined
in the ``typing`` module, plus these additional ones:

 * ``classmethod``
 * ``staticmethod``
 * ``property`` (including ``.setter`` and ``.deleter``)
 * ``abc.abstractmethod``
 * ``dataclasses.dataclass``
 * functions decorated with ``@typing.dataclass_transform``

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
"""""""""""""""""""""""""""

Stub files for libraries that support multiple Python versions can use version
checks to supply version-specific type hints. Stubs for different Python
versions should still conform to the most recent supported Python version's
syntax, as explained in the :ref:`stub-file-syntax` section above.

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

Stubs should avoid checking against ``sys.version_info.major`` directly and
should not use comparison operators other than ``<`` and ``>=``.

No::

    if sys.version_info.major >= 3:
        # Semantically the same as the first tuple check.

    if sys.version_info[0] >= 3:
        # This is also the same.

    if sys.version_info <= (2, 7):
        # This does not work because e.g. (2, 7, 1) > (2, 7).

Some stubs also may need to specify type hints for different platforms. Platform
checks must be equality comparisons between ``sys.platform`` and the name of a
platform as a string literal:

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
"""""

Enum classes are supported in stubs, regardless of the Python version targeted by
the stubs.

Enum members should be specified with an unannotated assignment, for example as
``x = 0`` or ``x = ...``. Non-member attributes should be specified with a type
annotation and no assigned value. See :ref:`enum-members` for details.

The Typeshed Project
^^^^^^^^^^^^^^^^^^^^

The `typeshed project <https://github.com/python/typeshed>`_ contains type
stubs for the standard library (vendored or handled specially by type checkers)
and type stubs for third-party libraries that don't ship their own type information
(typically distributed via PyPI). Policies regarding the
stubs collected there are decided separately and described in the project's
documentation.

.. _packaging-typed-libraries:

Type information in libraries
-----------------------------

(Originally specified in :pep:`561`.)

There are several motivations and methods of supporting typing in a package.
This specification recognizes three types of packages that users of typing wish to
create:

1. The package maintainer would like to add type information inline.

2. The package maintainer would like to add type information via stubs.

3. A third party or package maintainer would like to share stub files for
   a package, but the maintainer does not want to include them in the source
   of the package.

This specification aims to support all three scenarios and make them simple to add to
packaging and deployment.

The two major parts of this specification are the packaging specifications
and the resolution order for resolving module type information.


Packaging Type Information
^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to make packaging and distributing type information as simple and
easy as possible, packaging and distribution is done through existing
frameworks.

Package maintainers who wish to support type checking of their code MUST add
a marker file named ``py.typed`` to their package supporting typing. This marker applies
recursively: if a top-level package includes it, all its sub-packages MUST support
type checking as well.

To have this file including with the package, maintainers can use existing packaging
options such as ``package_data`` in ``setuptools``. For more details, see
:ref:`the guide to providing type annotations <providing-type-annotations>`.

For namespace packages (see :pep:`420`), the ``py.typed`` file should be in the
submodules of the namespace, to avoid conflicts and for clarity.

This specification does not support distributing typing information as part of
module-only distributions or single-file modules within namespace packages.

The single-file module should be refactored into a package
and indicate that the package supports typing as described
above.

Stub-only Packages
""""""""""""""""""

For package maintainers wishing to ship stub files containing all of their
type information, it is preferred that the ``*.pyi`` stubs are alongside the
corresponding ``*.py`` files. However, the stubs can also be put in a separate
package and distributed separately. Third parties can also find this method
useful if they wish to distribute stub files. The name of the stub package
MUST follow the scheme ``foopkg-stubs`` for type stubs for the package named
``foopkg``.

Note the name of the distribution (i.e. the project name on PyPI) containing
the package MAY be different than the mandated ``*-stubs`` package name.
The name of the distribution SHOULD NOT be ``types-*``, since this is
conventionally used for stub-only packages provided by typeshed.

For stub-only packages adding a ``py.typed`` marker is not
needed since the name ``*-stubs`` is enough to indicate it is a source of typing
information.

Third parties seeking to distribute stub files are encouraged to contact the
maintainer of the package about distribution alongside the package. If the
maintainer does not wish to maintain or package stub files or type information
:term:`inline`, then a third party stub-only package can be created.

In addition, stub-only distributions MAY indicate which version(s)
of the runtime package are targeted by indicating the runtime distribution's
version(s) through normal dependency data. For example, the
stub package ``flyingcircus-stubs`` can indicate the versions of the
runtime ``flyingcircus`` distribution it supports through ``dependencies``
field in ``pyproject.toml``.

For namespace packages (see :pep:`420`), stub-only packages should
use the ``-stubs`` suffix on only the root namespace package.
All stub-only namespace packages should omit ``__init__.pyi`` files. ``py.typed``
marker files are not necessary for stub-only packages, but similarly
to packages with inline types, if used, they should be in submodules of the namespace to
avoid conflicts and for clarity.

For example, if the ``pentagon`` and ``hexagon`` are separate distributions
installing within the namespace package ``shapes.polygons``
The corresponding types-only distributions should produce packages
laid out as follows::

    shapes-stubs
    └── polygons
        └── pentagon
            └── __init__.pyi

    shapes-stubs
    └── polygons
        └── hexagon
            └── __init__.pyi

Partial Stub Packages
"""""""""""""""""""""

Many stub packages will only have part of the type interface for libraries
completed, especially initially. For the benefit of type checking and code
editors, packages can be "partial". This means modules not found in the stub
package SHOULD be searched for in parts five and six of the module resolution
order below, namely :term:`inline` packages and any third-party stubs the type
checker chooses to vendor.

Type checkers should merge the stub package and runtime package
directories. This can be thought of as the functional equivalent of copying the
stub package into the same directory as the corresponding runtime package
and type checking the combined directory structure. Thus type
checkers MUST maintain the normal resolution order of checking ``*.pyi`` before
``*.py`` files.

If a stub package distribution is partial it MUST include ``partial\n`` in a
``py.typed`` file.  For stub-packages distributing within a namespace
package (see :pep:`420`), the ``py.typed`` file should be in the
submodules of the namespace.

Type checkers should treat namespace packages within stub-packages as
incomplete since multiple distributions may populate them.
Regular packages within namespace packages in stub-package distributions
are considered complete unless a ``py.typed`` with ``partial\n`` is included.

.. _mro:

Import resolution ordering
^^^^^^^^^^^^^^^^^^^^^^^^^^

The following is the order in which type checkers supporting this specification SHOULD
resolve modules containing type information:


1. :term:`Stubs <stub>` or Python source manually put in the beginning of the path. Type
   checkers SHOULD provide this to allow the user complete control of which
   stubs to use, and to patch broken stubs or :term:`inline` types from packages.
   In mypy the ``$MYPYPATH`` environment variable can be used for this.

2. User code - the files the type checker is running on.

3. Typeshed stubs for the standard library. These will usually be vendored by
   type checkers, but type checkers SHOULD provide an option for users to
   provide a path to a directory containing a custom or modified version of
   typeshed; if this option is provided, type checkers SHOULD use this as the
   canonical source for standard-library types in this step.

4. :term:`Stub <stub>` packages - these packages SHOULD supersede any installed inline
   package. They can be found in directories named ``foopkg-stubs`` for
   package ``foopkg``.

5. Packages with a ``py.typed`` marker file - if there is nothing overriding
   the installed package, *and* it opts into type checking, the types
   bundled with the package SHOULD be used (be they in ``.pyi`` type
   stub files or inline in ``.py`` files).

6. If the type checker chooses to additionally vendor any third-party stubs
   (from typeshed or elsewhere), these SHOULD come last in the module
   resolution order.

If typecheckers identify a stub-only namespace package without the desired module
in step 4, they should continue to step 5/6. Typecheckers should identify namespace packages
by the absence of ``__init__.pyi``.  This allows different subpackages to
independently opt for inline vs stub-only.

Type checkers that check a different Python version than the version they run
on MUST find the type information in the ``site-packages``/``dist-packages``
of that Python version. This can be queried e.g.
``pythonX.Y -c 'import site; print(site.getsitepackages())'``. It is also recommended
that the type checker allow for the user to point to a particular Python
binary, in case it is not in the path.

.. _import-conventions:

Import Conventions
------------------

By convention, certain import forms indicate to type checkers that an imported
symbol is re-exported and should be considered part of the importing module's
public interface. All other imported symbols are considered private by default.

The following import forms re-export symbols:

* ``import X as X`` (a redundant module alias): re-exports ``X``.
* ``from Y import X as X`` (a redundant symbol alias): re-exports ``X``.
* ``from Y import *``: re-exports all symbols in ``Y`` that do not begin with
  an underscore.
* ``from . import bar`` in an ``__init__`` module: re-exports ``bar`` if it does
  not begin with an underscore.
* ``from .bar import Bar`` in an ``__init__`` module: re-exports ``Bar`` if it
  does not begin with an underscore.
