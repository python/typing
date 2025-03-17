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
* They can be distributed separately from the package or module that they
  provide types for. The latter is referred to as the *implementation*.
  This allows stubs to be developed at a different pace or by different
  authors, which is especially useful when adding type annotations to
  existing packages.
* They can act as documentation, succinctly explaining the external
  API of a package, without including implementation details or private
  members.

Stub files use a subset of the constructs used in Python source files, as
described in :ref:`stub-file-supported-constructs` below. Type checkers should
parse a stub that uses only such constructs without error and not interpret any
construct in a manner contradictory to this specification. However, type
checkers are not required to implement checks for all of these constructs and
can elect to ignore unsupported ones. Additionally, type checkers can support
constructs not described here.

If a stub file is found for a module, the type checker should not read the
corresponding "real" module. See :ref:`mro` for more information.

.. _stub-file-syntax:

Syntax
^^^^^^

Stub files are syntactically valid Python files with a ``.pyi`` suffix. They
should be parseable (e.g., with :py:func:`ast.parse`) in all Python versions
that are supported by the implementation and that are still supported
by the CPython project. For example, defining a type alias using the
``type`` keyword is only accepted by the Python parser in Python 3.12 and later,
so stubs supporting Python 3.11 or earlier versions should not use this syntax.
This allows type checkers implemented in Python to parse stub files using
functionality from the standard library.
Type checkers may choose to support syntactic features from newer Python versions
in stub files, but stubs that rely on such features may not be portable to all
type checkers. Type checkers may also choose to support Python versions that
are no longer supported by CPython; if so, they cannot rely on standard library
functionality to parse stub files.

Type checkers should evaluate all :term:`annotation expressions <annotation expression>` as if they are quoted.
Consequently, forward references do not need to be quoted, and type system
features that do not depend on Python syntax changes are supported in stubs regardless
of the Python version supported. For example, the use of the ``|`` operator
to create unions (``X | Y``) was introduced in Python 3.10, but may be used
even in stubs that support Python 3.9 and older versions.

.. _stub-file-supported-constructs:

Supported Constructs
^^^^^^^^^^^^^^^^^^^^

Type checkers should fully support these constructs:

* All features from the ``typing`` module of the latest released Python version
  that use :ref:`supported syntax <stub-file-syntax>`
* Comments, including type declaration (``# type: X``) and error suppression
  (``# type: ignore``) comments
* Import statements, including the standard :ref:`import-conventions` and cyclic
  imports
* Aliases, including type aliases, at both the module and class level
* :ref:`Simple version and platform checks <version-and-platform-checks>`

The constructs in the following subsections may be supported in a more limited
fashion, as described below.

Value Expressions
"""""""""""""""""

In locations where value expressions can appear, such as the right-hand side of
assignment statements and function parameter defaults, type checkers should
support the following expressions:

* The ellipsis literal, ``...``, which can stand in for any value
* Any value that is a
  :ref:`legal parameter for typing.Literal <literal-legal-parameters>`
* Floating point literals, such as ``3.14``
* Complex literals, such as ``1 + 2j``

Module Level Attributes
"""""""""""""""""""""""

Type checkers should support module-level variable annotations, with and without
assignments::

    x: int
    x: int = 0
    x = 0  # type: int
    x = ...  # type: int

The :ref:`Literal shortcut using Final <literal-final-interactions>` should be
supported::

    x: Final = 0  # type is Literal[0]

When the type of a variable is omitted or disagrees from the assigned value,
type checker behavior is undefined::

    x = 0  # behavior undefined
    x: Final = ...  # behavior undefined
    x: int = ""  # behavior undefined

Classes
"""""""

Class definition syntax follows general Python syntax, but type checkers
are expected to understand only the following constructs in class bodies:

* The ellipsis literal ``...`` is used for empty class bodies. Using ``pass`` in
  class bodies is undefined.
* Instance attributes follow the same rules as module level attributes
  (see above).
* Method definitions (see below) and properties.
* Aliases.
* Inner class definitions.

Yes::

    class Simple: ...

    class Complex(Base):
        read_write: int
        @property
        def read_only(self) -> int: ...
        def do_stuff(self, y: str) -> None: ...
        doStuff = do_stuff
        IntList: TypeAlias = list[int]
        class Inner: ...

Functions and Methods
"""""""""""""""""""""

Function and method definition follows general Python syntax. Using a function
or method body other than the ellipsis literal is undefined::

    def foo(): ...  # compatible
    def bar(): pass  # behavior undefined

.. _stub-decorators:

Decorators
""""""""""

Type checkers are expected to understand the effects of all decorators defined
in the ``typing`` module, plus these additional ones:

 * ``classmethod``
 * ``staticmethod``
 * ``property`` (including ``.setter`` and ``.deleter``)
 * ``abc.abstractmethod``
 * ``dataclasses.dataclass``
 * ``warnings.deprecated``
 * functions decorated with ``@typing.dataclass_transform``

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

.. _library-interface:

Library interface (public and private symbols)
----------------------------------------------

If a ``py.typed`` module is present, a type checker will treat all modules
within that package (i.e. all files that end in ``.py`` or ``.pyi``) as
importable unless the file name begins with an underscore. These modules
comprise the supported interface for the library.

Each module exposes a set of symbols. Some of these symbols are
considered "private” — implementation details that are not part of the
library’s interface. Type checkers can use the following rules
to determine which symbols are visible outside of the package.

-  Symbols whose names begin with an underscore (but are not dunder
   names) are considered private.
-  Imported symbols are considered private by default. A fixed set of
   :ref:`import forms <import-conventions>` re-export imported symbols.
-  A module can expose an ``__all__`` symbol at the module level that
   provides a list of names that are considered part of the interface.
   This overrides all other rules above, allowing imported symbols or
   symbols whose names begin with an underscore to be included in the
   interface.
-  Local variables within a function (including nested functions) are
   always considered private.

The following idioms are supported for defining the values contained
within ``__all__``. These restrictions allow type checkers to statically
determine the value of ``__all__``.

-  ``__all__ = ('a', 'b')``
-  ``__all__ = ['a', 'b']``
-  ``__all__ += ['a', 'b']``
-  ``__all__ += submodule.__all__``
-  ``__all__.extend(['a', 'b'])``
-  ``__all__.extend(submodule.__all__)``
-  ``__all__.append('a')``
-  ``__all__.remove('a')``

.. _import-conventions:

Import Conventions
------------------

By convention, certain import forms indicate to type checkers that an imported
symbol is re-exported and should be considered part of the importing module's
public interface. All other imported symbols are considered private by default.

The following import forms re-export symbols:

* ``import X as X`` (a redundant module alias): re-exports ``X``.
* ``from Y import X as X`` (a redundant symbol alias): re-exports ``X``.
* ``from Y import *``: if ``Y`` defines a module-level ``__all__`` list,
  re-exports all names in ``__all__``; otherwise, re-exports  all public symbols
  in ``Y``'s global scope.
