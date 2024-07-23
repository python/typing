.. _writing_stubs:

**********************************
Writing and Maintaining Stub Files
**********************************

Stub files are a means of providing type information for Python modules.
For a full reference, refer to :ref:`stub-files`.

Maintaining stubs can be a little cumbersome because they are separated from the
implementation. This page lists some tools that make writing and maintaining
stubs less painful, as well as some best practices on stub contents and style.

Tools for generating stubs
==========================

stubgen
-------

stubgen is a tool bundled with `mypy <https://github.com/python/mypy>`__
that can be used to generate basic stubs. These stubs serve as a
basic starting point; most types will default to ``Any``.

.. code-block:: console

    stubgen -p my_great_package

For more details, see `stubgen docs <https://mypy.readthedocs.io/en/stable/stubgen.html>`__.

pyright
-------

pyright contains a tool that generates basic stubs. Like stubgen, these generated
stubs serve more as a starting point.

.. code-block:: console

    pyright --createstub my_great_package

For more details, see `pyright docs <https://github.com/microsoft/pyright/blob/main/docs/type-stubs.md#generating-type-stubs-from-command-line>`__.

monkeytype
----------

monkeytype takes a slightly different approach — you run your code (perhaps via
your tests) and monkeytype collects the types it observes at runtime to generate
stubs.

.. code-block:: console

    monkeytype run script.py
    monkeytype stub my_great_package

For more details, see `monkeytype docs <https://monkeytype.readthedocs.io/en/latest/>`__.

Tools for maintaining stubs
===========================

stubtest
--------

stubtest is a tool bundled with `mypy <https://github.com/python/mypy>`__.

stubtest finds inconsistencies between stub files and the implementation. It
does this by comparing stub definitions to what it finds from importing your
code and using runtime introspection (via the ``inspect`` module).

.. code-block:: console

    stubtest my_great_package

For more details, see `stubtest docs <https://mypy.readthedocs.io/en/stable/stubtest.html>`__.

flake8-pyi
----------

flake8-pyi is a `flake8 <https://flake8.pycqa.org/en/latest/>`__ plugin that
lints common issues in stub files.

.. code-block:: console

    flake8 my_great_package

For more details, see `flake8-pyi docs <https://github.com/PyCQA/flake8-pyi>`__.

Running a type checker on the stubs
-----------------------------------

Simply running a type checker on the stubs can catch several issues, from simple
things like detecting missing annotations to more complex things like ensuring
Liskov substitutability or detecting problematic overloads.

It may be instructive to examine `typeshed <https://github.com/python/typeshed/>`__'s
`setup for testing stubs <https://github.com/python/typeshed/blob/main/tests/README.md>`__.

..
   TODO: consider adding examples and configurations for specific type checkers

Type checking usage of your package
-----------------------------------

If you have access to a codebase that uses your package — perhaps tests for your
package — running a type checker against it can help you detect issues,
particularly with false positives.

If your package has some particularly complex aspects, you could even consider
writing dedicated typing tests for tricky definitions. For more details, see
:ref:`testing`.

Stub Content
============

This section documents best practices on what elements to include or
leave out of stub files.

Modules excluded fom stubs
--------------------------

Not all modules should be included into stubs.

It is recommended to exclude:

1. Implementation details, with `multiprocessing/popen_spawn_win32.py <https://github.com/python/cpython/blob/main/Lib/multiprocessing/popen_spawn_win32.py>`_ as a notable example
2. Modules that are not supposed to be imported, such as ``__main__.py``
3. Protected modules that start with a single ``_`` char. However, when needed protected modules can still be added (see :ref:`undocumented-objects` section below)

Public Interface
----------------

Stubs should include the complete public interface (classes, functions,
constants, etc.) of the module they cover, but it is not always
clear exactly what is part of the interface.

The following should always be included:

* All objects listed in the module's documentation.
* All objects included in ``__all__`` (if present).

Other objects may be included if they are not prefixed with an underscore
or if they are being used in practice. (See the next section.)

.. _undocumented-objects:

Undocumented Objects
--------------------

Undocumented objects may be included as long as they are marked with a comment
of the form ``# undocumented``.

Example::

    def list2cmdline(seq: Sequence[str]) -> str: ...  # undocumented

Such undocumented objects are allowed because omitting objects can confuse
users. Users who see an error like "module X has no attribute Y" will
not know whether the error appeared because their code had a bug or
because the stub is wrong. Although it may also be helpful for a type
checker to point out usage of private objects, false negatives (no errors for
wrong code) are preferable over false positives (type errors
for correct code). In addition, even for private objects a type checker
can be helpful in pointing out that an incorrect type was used.

``__all__``
------------

A stub file should contain an ``__all__`` variable if and only if it also
present at runtime. In that case, the contents of ``__all__`` should be
identical in the stub and at runtime. If the runtime dynamically adds
or removes elements (for example if certain functions are only available on
some platforms), include all possible elements in the stubs.

Stub-Only Objects
-----------------

Definitions that do not exist at runtime may be included in stubs to aid in
expressing types. Sometimes, it is desirable to make a stub-only class available
to a stub's users — for example, to allow them to type the return value of a
public method for which a library does not provided a usable runtime type::

  from typing import Protocol

  class _Readable(Protocol):
      def read(self) -> str: ...

  def get_reader() -> _Readable: ...

Structural Types
----------------

As seen in the example with ``_Readable`` in the previous section, a common use
of stub-only objects is to model types that are best described by their
structure. These objects are called protocols (:pep:`544`), and it is encouraged
to use them freely to describe simple structural types.

It is `recommended <#private-definitions>`_ to prefix stub-only object names with ``_``.

Incomplete Stubs
----------------

Partial stubs can be useful, especially for larger packages, but they should
follow the following guidelines:

* Included functions and methods should list all arguments, but the arguments
  can be left unannotated.
* Do not use ``Any`` to mark unannotated arguments or return values.
* Partial classes should include a ``__getattr__()`` method marked with an
  ``# incomplete`` comment (see example below).
* Partial modules (i.e. modules that are missing some or all classes,
  functions, or attributes) should include a top-level ``__getattr__()``
  function marked with an ``# incomplete`` comment (see example below).
* Partial packages (i.e. packages that are missing one or more sub-modules)
  should have a ``__init__.pyi`` stub that is marked as incomplete (see above).
  A better alternative is to create empty stubs for all sub-modules and
  mark them as incomplete individually.

Example of a partial module with a partial class ``Foo`` and a partially
annotated function ``bar()``::

    def __getattr__(name: str) -> Any: ...  # incomplete

    class Foo:
        def __getattr__(self, name: str) -> Any: ... # incomplete
        x: int
        y: str

    def bar(x: str, y, *, z=...): ...

The ``# incomplete`` comment is mainly intended as a reminder for stub
authors, but can be used by tools to flag such items.

Attribute Access
----------------

Python has several methods for customizing attribute access: ``__getattr__``,
``__getattribute__``, ``__setattr__``, and ``__delattr__``. Of these,
``__getattr__`` and ``__setattr___`` should sometimes be included in stubs.

In addition to marking incomplete definitions, ``__getattr__`` should be
included when a class or module allows any name to be accessed. For example, consider
the following class::

  class Foo:
      def __getattribute__(self, name):
          return self.__dict__.setdefault(name)

An appropriate stub definition is::

  from typing import Any

  class Foo:
      def __getattr__(self, name: str) -> Any | None: ...

Note that only ``__getattr__``, not ``__getattribute__``, is guaranteed to be
supported in stubs.

On the other hand, ``__getattr__`` should be omitted even if the source code
includes it, if only limited names are allowed. For example, consider this class::

  class ComplexNumber:
      def __init__(self, n):
          self._n = n
      def __getattr__(self, name):
          if name in ("real", "imag"):
              return getattr(self._n, name)
          raise AttributeError(name)

In this case, the stub should list the attributes individually::

  class ComplexNumber:
      @property
      def real(self) -> float: ...
      @property
      def imag(self) -> float: ...
      def __init__(self, n: complex) -> None: ...

``__setattr___`` should be included when a class allows any name to be set and
restricts the type. For example::

  class IntHolder:
      def __setattr__(self, name, value):
          if isinstance(value, int):
              return super().__setattr__(name, value)
          raise ValueError(value)

A good stub definition would be::

  class IntHolder:
      def __setattr__(self, name: str, value: int) -> None: ...

``__delattr__`` should not be included in stubs.

Finally, even in the presence of ``__getattr__`` and ``__setattr__``, it is
still recommended to separately define known attributes.

Constants
---------

When the value of a constant is important, annotate it using ``Literal``
instead of its type.

Yes::

    TEL_LANDLINE: Literal["landline"]
    TEL_MOBILE: Literal["mobile"]
    DAY_FLAG: Literal[0x01]
    NIGHT_FLAG: Literal[0x02]

No::

    TEL_LANDLINE: str
    TEL_MOBILE: str
    DAY_FLAG: int
    NIGHT_FLAG: int

Documentation or Implementation
-------------------------------

Sometimes a library's documented types will differ from the actual types in the
code. In such cases, stub authors should use their best judgment. Consider these
two examples::

  def print_elements(x):
      """Print every element of list x."""
      for y in x:
          print(y)

  def maybe_raise(x):
      """Raise an error if x (a boolean) is true."""
      if x:
          raise ValueError()

The implementation of ``print_elements`` takes any iterable, despite the
documented type of ``list``. In this case, annotate the argument as
``Iterable[Any]``, to follow the :ref:`best practice<argument-return-practices>`
of preferring abstract types for arguments.

For ``maybe_raise``, on the other hand, it is better to annotate the argument as
``bool`` even though the implementation accepts any object. This guards against
common mistakes like unintentionally passing in ``None``.

If in doubt, consider asking the library maintainers about their intent.

Style Guide
===========

The recommendations in this section are aimed at stub authors who wish to
provide a consistent style for stubs. Type checkers should not reject stubs that
do not follow these recommendations, but linters can warn about them.

Stub files should generally follow the Style Guide for Python Code (:pep:`8`)
and the :ref:`best-practices`. There are a few exceptions, outlined below, that take the
different structure of stub files into account and aim to create
more concise files.

Maximum Line Length
-------------------

Stub files should be limited to 130 characters per line.

Blank Lines
-----------

Do not use empty lines between functions, methods, and fields, except to
group them with one empty line. Use one empty line around classes with non-empty
bodies. Do not use empty lines between body-less classes, except for grouping.

Yes::

    def time_func() -> None: ...
    def date_func() -> None: ...

    def ip_func() -> None: ...

    class Foo:
        x: int
        y: int
        def __init__(self) -> None: ...

    class MyError(Exception): ...
    class AnotherError(Exception): ...

No::

    def time_func() -> None: ...

    def date_func() -> None: ...  # do no leave unnecessary empty lines

    def ip_func() -> None: ...


    class Foo:  # leave only one empty line above
        x: int
    class MyError(Exception): ...  # leave an empty line between the classes

Module Level Attributes
-----------------------

Do not unnecessarily use an assignment for module-level attributes.

Yes::

    CONST: Literal["const"]
    x: int
    y: Final = 0  # this assignment conveys additional type information

No::

    CONST = "const"
    x: int = 0
    y: float = ...
    z = 0  # type: int
    a = ...  # type: int

.. _stub-style-classes:

Classes
-------

Classes without bodies should use the ellipsis literal ``...`` in place
of the body on the same line as the class definition.

Yes::

    class MyError(Exception): ...

No::

    class MyError(Exception):
        ...
    class AnotherError(Exception): pass

Instance attributes and class variables follow the same recommendations as
module level attributes:

Yes::

    class Foo:
        c: ClassVar[str]
        x: int

    class Color(Enum):
        # An assignment with no type annotation is a convention used to indicate
	# an enum member.
        RED = 1

No::

    class Foo:
        c: ClassVar[str] = ""
        d: ClassVar[int] = ...
        x = 4
        y: int = ...

Functions and Methods
---------------------

For keyword-only and positional-or-keyword arguments, use the same
argument names as in the implementation, because otherwise using
keyword arguments will fail.

Use the ellipsis literal ``...`` in place of actual default argument
values. Use an explicit ``X | None`` annotation instead of
a ``None`` default.

Yes::

    def foo(x: int = ...) -> None: ...
    def bar(y: str | None = ...) -> None: ...

No::

    def foo(x: int = 0) -> None: ...
    def bar(y: str = None) -> None: ...
    def baz(z: str | None = None) -> None: ...

Do not annotate ``self`` and ``cls`` in method definitions, except when
referencing a type variable.

Yes::

    _T = TypeVar("_T")

    class Foo:
        def bar(self) -> None: ...
        @classmethod
        def create(cls: type[_T]) -> _T: ...

No::

    class Foo:
        def bar(self: Foo) -> None: ...
        @classmethod
        def baz(cls: type[Foo]) -> int: ...

The bodies of functions and methods should consist of only the ellipsis
literal ``...`` on the same line as the closing parenthesis and colon.

Yes::

    def to_int1(x: str) -> int: ...
    def to_int2(
        x: str,
    ) -> int: ...

No::

    def to_int1(x: str) -> int:
        return int(x)
    def to_int2(x: str) -> int:
        ...
    def to_int3(x: str) -> int: pass

.. _private-definitions:

Private Definitions
-------------------

Type variables, type aliases, and other definitions that don't exist at
runtime should be marked as private by prefixing them
with an underscore.

Yes::

    _T = TypeVar("_T")
    _DictList: TypeAlias = dict[str, list[int | None]]

No::

    T = TypeVar("T")
    DictList: TypeAlias = dict[str, list[int | None]]

Language Features
-----------------

Use the latest language features available, even for stubs targeting older
Python versions. Do not use quotes around forward references and do not use
``__future__`` imports. See :ref:`stub-file-syntax` for more information.

Yes::

    class Py35Class:
        x: int
        forward_reference: OtherClass

    class OtherClass: ...

No::

    class Py35Class:
        x = 0  # type: int
        forward_reference: 'OtherClass'

    class OtherClass: ...

NamedTuple and TypedDict
------------------------

Use the class-based syntax for ``typing.NamedTuple`` and
``typing.TypedDict``, following the :ref:`stub-style-classes` section of this style guide.

Yes::

    from typing import NamedTuple, TypedDict

    class Point(NamedTuple):
        x: float
        y: float

    class Thing(TypedDict):
        stuff: str
        index: int

No::

    from typing import NamedTuple, TypedDict
    Point = NamedTuple("Point", [('x', float), ('y', float)])
    Thing = TypedDict("Thing", {'stuff': str, 'index': int})
