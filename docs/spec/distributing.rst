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

Stub files that only use the constructs described in :ref:`Supported Constructs`
below should work with all type checkers that conform to this specification. A
conformant type checker will parse a stub that only uses such constructs without
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
the ``type`` soft keyword from :pep:`695`, introduced in Python 3.12, util
Python 3.11 reaches end-of-life in October 2027.

Stubs are treated as if ``from __future__ import annotations`` is enabled. In
particular, built-in generics, pipe union syntax (``X | Y``), and forward
references can be used.

Type checkers should have a configurable search path for stub files. If a stub
file is found, the type checker should not read the corresponding "real" module.
See :ref:`Import resolution ordering` for more information.


Supported Constructs
^^^^^^^^^^^^^^^^^^^^

This section lists constructs that type checkers will accept in stub files. Stub
authors can safely use these constructs. If a construct is marked as
"unspecified", type checkers may handle it as they best see fit or report an
error. Linters should usually flag those constructs. Stub authors should avoid
using them to ensure compatibility across type checkers.

Unless otherwise mentioned, stub files support all features from the ``typing``
module of the latest released Python version. If a stub uses typing features
from a later Python version than what the implementation supports, these
features can be imported from ``typing_extensions`` instead of ``typing``.

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

Classes
"""""""

Functions and Methods
"""""""""""""""""""""

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

Version and Platform Checks
"""""""""""""""""""""""""""

Stub files for libraries that support multiple Python versions can use version
checks to supply version-specific type hints. Stubs for different Python
versions should still conform to the most recent supported Python version's
syntax, as explain in the :ref:`Syntax` section above.

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
