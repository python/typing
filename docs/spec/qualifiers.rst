.. _`type-qualifiers`:

Type qualifiers
===============

This chapter describes the behavior of some :term:`type qualifiers <type qualifier>`.
Additional type qualifiers are covered in other chapters:

* :ref:`ClassVar <classvar>`
* :ref:`NotRequired <notrequired>`
* :ref:`ReadOnly <readonly>`
* :ref:`Required <required>`

.. _`at-final`:

``@final``
----------

(Originally specified in :pep:`591`.)

The ``typing.final`` decorator is used to restrict the use of
inheritance and overriding.

A type checker should prohibit any class decorated with ``@final``
from being subclassed and any method decorated with ``@final`` from
being overridden in a subclass. The method decorator version may be
used with all of instance methods, class methods, static methods, and properties.

For example::

    from typing import final

    @final
    class Base:
        ...

    class Derived(Base):  # Error: Cannot inherit from final class "Base"
        ...

and::

    from typing import final

    class Base:
        @final
        def foo(self) -> None:
            ...

    class Derived(Base):
        def foo(self) -> None:  # Error: Cannot override final attribute "foo"
                                # (previously declared in base class "Base")
            ...


For overloaded methods, ``@final`` should be placed on the
implementation (or on the first overload, for stubs)::

   from typing import Any, overload

   class Base:
       @overload
       def method(self) -> None: ...
       @overload
       def method(self, arg: int) -> int: ...
       @final
       def method(self, x=None):
           ...

It is an error to use ``@final`` on a non-method function.

.. _`uppercase-final`:

``Final``
---------

(Originally specified in :pep:`591`.)

The ``typing.Final`` :term:`type qualifier` is used to indicate that a
variable or attribute should not be reassigned, redefined, or overridden.

Syntax
^^^^^^

``Final`` may be used in one of several forms:

* With an explicit type, using the syntax ``Final[<type>]``. Example::

    ID: Final[float] = 1

* With no type annotation. Example::

    ID: Final = 1

  The typechecker should apply its usual type inference mechanisms to
  determine the type of ``ID`` (here, likely, ``int``). Note that unlike for
  generic classes this is *not* the same as ``Final[Any]``.

* In class bodies and stub files you can omit the right hand side and just write
  ``ID: Final[float]``.  If the right hand side is omitted, there must
  be an explicit type argument to ``Final``.

* Finally, as ``self.id: Final = 1`` (also optionally with a type in
  square brackets). This is allowed *only* in ``__init__`` methods, so
  that the final instance attribute is assigned only once when an
  instance is created.


Semantics and examples
^^^^^^^^^^^^^^^^^^^^^^

The two main rules for defining a final name are:

* There can be *at most one* final declaration per module or class for
  a given attribute. There can't be separate class-level and instance-level
  constants with the same name.

* There must be *exactly one* assignment to a final name.

This means a type checker should prevent further assignments to final
names in type-checked code::

   from typing import Final

   RATE: Final = 3000

   class Base:
       DEFAULT_ID: Final = 0

   RATE = 300  # Error: can't assign to final attribute
   Base.DEFAULT_ID = 1  # Error: can't override a final attribute

Note that a type checker need not allow ``Final`` declarations inside loops
since the runtime will see multiple assignments to the same variable in
subsequent iterations.

Additionally, a type checker should prevent final attributes from
being overridden in a subclass::

   from typing import Final

   class Window:
       BORDER_WIDTH: Final = 2.5
       ...

   class ListView(Window):
       BORDER_WIDTH = 3  # Error: can't override a final attribute

A final attribute declared in a class body without an initializer must
be initialized in the ``__init__`` method (except in stub files)::

   class ImmutablePoint:
       x: Final[int]
       y: Final[int]  # Error: final attribute without an initializer

       def __init__(self) -> None:
           self.x = 1  # Good

The generated ``__init__`` method of :doc:`dataclasses` qualifies for this
requirement: a bare ``x: Final[int]`` is permitted in a dataclass body, because
the generated ``__init__`` will initialize ``x``.

Type checkers should infer a final attribute that is initialized in a class
body as being a class variable, except in the case of :doc:`dataclasses`, where
``x: Final[int] = 3`` creates a dataclass field and instance-level final
attribute ``x`` with default value ``3``; ``x: ClassVar[Final[int]] = 3`` is
necessary to create a final class variable with value ``3``. In
non-dataclasses, combining ``ClassVar`` and ``Final`` is redundant, and type
checkers may choose to warn or error on the redundancy.

``Final`` may only be used in assignments or variable annotations. Using it in
any other position is an error. In particular, ``Final`` can't be used in
annotations for function arguments::

   x: list[Final[int]] = []  # Error!

   def fun(x: Final[List[int]]) ->  None:  # Error!
       ...

``Final`` may be wrapped only by other type qualifiers (e.g. ``ClassVar`` or
``Annotation``). It cannot be used in a type parameter (e.g.
``list[Final[int]]`` is not permitted.)

Note that declaring a name as final only guarantees that the name will
not be re-bound to another value, but does not make the value
immutable. Immutable ABCs and containers may be used in combination
with ``Final`` to prevent mutating such values::

   x: Final = ['a', 'b']
   x.append('c')  # OK

   y: Final[Sequence[str]] = ['a', 'b']
   y.append('x')  # Error: "Sequence[str]" has no attribute "append"
   z: Final = ('a', 'b')  # Also works


Type checkers should treat uses of a final name that was initialized
with a literal as if it was replaced by the literal. For example, the
following should be allowed::

   from typing import NamedTuple, Final

   X: Final = "x"
   Y: Final = "y"
   N = NamedTuple("N", [(X, int), (Y, int)])

.. _`annotated`:

``Annotated``
-------------

(Originally specified by :pep:`593`.)

Syntax
^^^^^^

``Annotated`` is parameterized with a *base expression* and at least one
Python value representing associated *metadata*::

    from typing import Annotated

    Annotated[BaseExpr, Metadata1, Metadata2, ...]

Here are the specific details of the syntax:

* The base expression (the first argument to ``Annotated``) must be valid
  in the context where it is being used:

    * If ``Annotated`` is used in a place where arbitrary
      :term:`annotation expressions <annotation expression>` are allowed,
      the base expression may be an annotation expression.
    * Otherwise, the base expression must be a valid :term:`type expression`.

* Multiple metadata elements are supported (``Annotated`` supports variadic
  arguments)::

    Annotated[int, ValueRange(3, 10), ctype("char")]

* There must be at least one metadata element (``Annotated[int]`` is not valid)

* The order of the metadata is preserved and matters for equality
  checks::

    Annotated[int, ValueRange(3, 10), ctype("char")] != Annotated[
        int, ctype("char"), ValueRange(3, 10)
    ]

* Nested ``Annotated`` types are flattened, with metadata ordered
  starting with the innermost ``Annotated`` expression::

    Annotated[Annotated[int, ValueRange(3, 10)], ctype("char")] == Annotated[
        int, ValueRange(3, 10), ctype("char")
    ]

* Duplicated metadata elements are not removed::

    Annotated[int, ValueRange(3, 10)] != Annotated[
        int, ValueRange(3, 10), ValueRange(3, 10)
    ]

* ``Annotated`` can be used in definition of nested and generic aliases,
  but only if it wraps a :term:`type expression`::

    T = TypeVar("T")
    Vec = Annotated[list[tuple[T, T]], MaxLen(10)]
    V = Vec[int]

    V == Annotated[list[tuple[int, int]], MaxLen(10)]

* As with most :term:`special forms <special form>`, ``Annotated`` is not type compatible with
  ``type`` or ``type[T]``::

    v1: type[int] = Annotated[int, ""]  # Type error

    SmallInt: TypeAlias = Annotated[int, ValueRange(0, 100)]
    v2: type[Any] = SmallInt  # Type error

* An attempt to call ``Annotated`` (whether parameterized or not) should be
  treated as a type error by type checkers::

    Annotated()  # Type error
    Annotated[int, ""](0)  # Type error

    SmallInt = Annotated[int, ValueRange(0, 100)]
    SmallInt(1)  # Type error

:pep:`593` and an earlier version of this specification used the term
"annotations" instead of "metadata" for the extra arguments to
``Annotated``. The term "annotations" is deprecated to avoid confusion
with the parameter, return, and variable annotations that are part of
the Python syntax.

Meaning
^^^^^^^

The metadata provided by ``Annotated`` can be used for either static
or runtime analysis. If a library (or tool) encounters an instance of
``Annotated[T, x]`` and has no special logic for metadata element ``x``, it
should ignore it and treat the expression as equivalent to ``T``. Thus, in general,
any :term:`type expression` or :term:`annotation expression` may be
wrapped in ``Annotated`` without changing the meaning of the
wrapped expression. However, type
checkers may additionally choose to recognize particular metadata elements and use
them to implement extensions to the standard type system.

``Annotated`` metadata may apply either to the base expression or to the symbol
being annotated, or even to some other aspect of the program.

Consuming metadata
^^^^^^^^^^^^^^^^^^

Ultimately, deciding how to interpret the metadata (if
at all) is the responsibility of the tool or library encountering the
``Annotated`` type. A tool or library encountering an ``Annotated`` type
can scan through the metadata to determine if they are of interest
(e.g., using ``isinstance()``).

**Unknown metadata:** When a tool or a library does not support
metadata or encounters an unknown metadata element, it should ignore it
and treat the annotation as the base expression.

**Namespacing metadata:** Namespaces are not needed for metadata since
the class of the metadata object acts as a namespace.

**Multiple metadata elements:** It's up to the tool consuming the metadata
to decide whether the client is allowed to have several metadata elements on
one annotation and how to merge those elements.

Since the ``Annotated`` type allows you to put several metadata elements of
the same (or different) type(s) on any annotation, the tools or libraries
consuming the metadata are in charge of dealing with potential
duplicates. For example, if you are doing value range analysis you might
allow this::

    T1 = Annotated[int, ValueRange(-10, 5)]
    T2 = Annotated[T1, ValueRange(-20, 3)]

Flattening nested annotations, this translates to::

    T2 = Annotated[int, ValueRange(-10, 5), ValueRange(-20, 3)]

Aliases & Concerns over verbosity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Writing ``typing.Annotated`` everywhere can be quite verbose;
fortunately, the ability to alias types means that in practice we
don't expect clients to have to write lots of boilerplate code::

    type Const[T] = Annotated[T, my_annotations.CONST]

    class C:
        def const_method(self, x: Const[list[int]]) -> int:
            ...
