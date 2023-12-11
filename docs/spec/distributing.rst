.. _distributing-type:

Distributing type information
=============================

Stub files
----------

Stub files are files containing type hints that are only for use by
the type checker, not at runtime.  There are several use cases for
stub files:

* Extension modules

* Third-party modules whose authors have not yet added type hints

* Standard library modules for which type hints have not yet been
  written

* Modules that must be compatible with Python 2 and 3

* Modules that use annotations for other purposes

Stub files have the same syntax as regular Python modules.  There is one
feature of the ``typing`` module that is different in stub files:
the ``@overload`` decorator described below.

The type checker should only check function signatures in stub files;
It is recommended that function bodies in stub files just be a single
ellipsis (``...``).

The type checker should have a configurable search path for stub files.
If a stub file is found the type checker should not read the
corresponding "real" module.

While stub files are syntactically valid Python modules, they use the
``.pyi`` extension to make it possible to maintain stub files in the
same directory as the corresponding real module.  This also reinforces
the notion that no runtime behavior should be expected of stub files.

Additional notes on stub files:

* Modules and variables imported into the stub are not considered
  exported from the stub unless the import uses the ``import ... as
  ...`` form or the equivalent ``from ... import ... as ...`` form.
  (*UPDATE:* To clarify, the intention here is that only names
  imported using the form ``X as X`` will be exported, i.e. the name
  before and after ``as`` must be the same.)

* However, as an exception to the previous bullet, all objects
  imported into a stub using ``from ... import *`` are considered
  exported.  (This makes it easier to re-export all objects from a
  given module that may vary by Python version.)

* Just like in `normal Python files <https://docs.python.org/3/reference/import.html#submodules>`_, submodules
  automatically become exported attributes of their parent module
  when imported. For example, if the ``spam`` package has the
  following directory structure::

      spam/
          __init__.pyi
          ham.pyi

  where ``__init__.pyi`` contains a line such as ``from . import ham``
  or ``from .ham import Ham``, then ``ham`` is an exported attribute
  of ``spam``.

* Stub files may be incomplete. To make type checkers aware of this, the file
  can contain the following code::

    def __getattr__(name) -> Any: ...

  Any identifier not defined in the stub is therefore assumed to be of type
  ``Any``.

The Typeshed Repo
^^^^^^^^^^^^^^^^^

There is a `shared repository <https://github.com/python/typeshed>`_ where useful stubs are being
collected.  Policies regarding the stubs collected here are
decided separately and reported in the repo's documentation.


Type information in libraries
-----------------------------

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
type checking as well. To have this file installed with the package,
maintainers can use existing packaging options such as ``package_data`` in
distutils, shown below.

Distutils option example::

    setup(
        ...,
        package_data = {
            'foopkg': ['py.typed'],
        },
        ...,
        )

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
``foopkg``. Note that for stub-only packages adding a ``py.typed`` marker is not
needed since the name ``*-stubs`` is enough to indicate it is a source of typing
information.

Third parties seeking to distribute stub files are encouraged to contact the
maintainer of the package about distribution alongside the package. If the
maintainer does not wish to maintain or package stub files or type information
inline, then a third party stub-only package can be created.

In addition, stub-only distributions SHOULD indicate which version(s)
of the runtime package are supported by indicating the runtime distribution's
version(s) through normal dependency data. For example, the
stub package ``flyingcircus-stubs`` can indicate the versions of the
runtime ``flyingcircus`` distribution it supports through ``install_requires``
in distutils-based tools, or the equivalent in other packaging tools. Note that
in pip 9.0, if you update ``flyingcircus-stubs``, it will update
``flyingcircus``. In pip 9.0, you can use the
``--upgrade-strategy=only-if-needed`` flag. In pip 10.0 this is the default
behavior.

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
package SHOULD be searched for in parts four and five of the module resolution
order above, namely inline packages and typeshed.

Type checkers should merge the stub package and runtime package or typeshed
directories. This can be thought of as the functional equivalent of copying the
stub package into the same directory as the corresponding runtime package or
typeshed folder and type checking the combined directory structure. Thus type
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

Import resolutiong ordering
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following is the order in which type checkers supporting this specification SHOULD
resolve modules containing type information:


1. Stubs or Python source manually put in the beginning of the path. Type
   checkers SHOULD provide this to allow the user complete control of which
   stubs to use, and to patch broken stubs/inline types from packages.
   In mypy the ``$MYPYPATH`` environment variable can be used for this.

2. User code - the files the type checker is running on.

3. Stub packages - these packages SHOULD supersede any installed inline
   package. They can be found at ``foopkg-stubs`` for package ``foopkg``.

4. Packages with a ``py.typed`` marker file - if there is nothing overriding
   the installed package, *and* it opts into type checking, the types
   bundled with the package SHOULD be used (be they in ``.pyi`` type
   stub files or inline in ``.py`` files).

5. Typeshed (if used) - Provides the stdlib types and several third party
   libraries.

If typecheckers identify a stub-only namespace package without the desired module
in step 3, they should continue to step 4/5. Typecheckers should identify namespace packages
by the absence of ``__init__.pyi``.  This allows different subpackages to
independently opt for inline vs stub-only.

Type checkers that check a different Python version than the version they run
on MUST find the type information in the ``site-packages``/``dist-packages``
of that Python version. This can be queried e.g.
``pythonX.Y -c 'import site; print(site.getsitepackages())'``. It is also recommended
that the type checker allow for the user to point to a particular Python
binary, in case it is not in the path.
