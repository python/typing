.. _`type-system-concepts`:

Type system concepts
====================

Static, dynamic, and gradual typing
-----------------------------------

A **statically typed** programming language runs a type checker before running
a program. The program is required to be well typed according to the language's
type system. The type system assigns a type to all expressions in the language
and verifies that their uses obey the typing rules. Normally, a program that is
not well typed (i.e., one that contains a type error) will not run. Java and
C++ are examples of statically typed object-oriented languages.

A **dynamically typed** programming language does not run a type checker before
running a program. Instead, it checks the types of values before performing
operations on them at runtime. This is not to say that the language is
"untyped". Values at runtime have a type and their uses obey typing rules. Not
every operation will be checked, but certain primitive operations in the
language such as attribute access or arithmetic are. Python is a
dynamically typed language.

**Gradual typing** is a way to combine static and dynamic typing.
Type-annotated Python allows opting in to static type checking at a fine level
of granularity, so that some type errors can be caught statically, without
running the program. Variables, parameters, and returns can optionally be given
static type annotations. Even within the type of a single data structure,
static type checking is optional and granular. For example, a dictionary can be
annotated to enable static checking of the key type but only have dynamic
runtime checking of the value type.

A **gradual** type system is one in which a special "unknown" or "dynamic" type
is used to describe names or expressions whose types are not known statically.
In Python, this type is spelled :ref:`Any`. Because :ref:`!Any` indicates a
statically unknown type, the static type checker can't check type correctness
of operations on expressions typed as :ref:`!Any`. These operations are still
dynamically checked, via the Python runtime's usual dynamic checking.

The Python type system also uses ``...`` within :ref:`Callable` types and
within ``tuple[Any, ...]`` (see :ref:`tuples`) to indicate a statically unknown
component of a type. The detailed rules for these usages are discussed in their
respective sections of the specification. Collectively, along with :ref:`Any`,
these are :term:`gradual forms <gradual form>`.

This specification describes a gradual type system for Python.

Fully static and gradual types
------------------------------

We will refer to types that do not contain a :term:`gradual form` as a sub-part
as **fully static types**.

A **gradual type** can be a fully static type, :ref:`Any` itself, or a type
that contains a gradual form as a sub-part. All Python types are gradual types;
fully static types are a subset.

Fully static types
~~~~~~~~~~~~~~~~~~

A fully static type denotes a set of potential runtime values. For instance,
the fully static type ``object`` is the set of all Python objects. The fully
static type ``bool`` is the set of values ``{ True, False }``. The fully static
type ``str`` is the set of all Python strings; more precisely, the set of all
Python objects whose runtime type (``__class__`` attribute) is either ``str``
or a class that inherits directly or indirectly from ``str``. A :ref:`Protocol
<Protocols>` denotes the set of all objects which share a certain set of
attributes and/or methods.

If an object ``v`` is a member of the set of objects denoted by a fully static
type ``T``, we can say that ``v`` is a "member of" the type ``T``, or ``v``
"inhabits" ``T``.

Gradual types
~~~~~~~~~~~~~

:ref:`Any` represents an unknown static type. It denotes some unknown set of
runtime values.

This may appear similar to the fully static type ``object``, which represents
the set of all Python objects, but it is quite different.

If an expression has the type ``object``, a static type checker should ensure
that operations on the expression are valid for all Python objects, or else
emit a static type error. This allows very few operations! For example, if
``x`` is typed as ``object``, ``x.foo`` should be a static type error because
not all Python objects have an attribute ``foo``.

An expression typed as :ref:`Any`, on the other hand, should be assumed to have
_some_ specific static type, but _which_ static type is not known. A static
type checker should not emit static type errors on an expression or statement
if :ref:`!Any` might represent a static type which would avoid the error. (This
is defined more precisely below, in terms of materialization and
assignability.)

Similarly, a type such as ``tuple[int, Any]`` (see :ref:`tuples`) or ``int |
Any`` (see :ref:`union-types`) does not represent a single set of Python
objects; rather, it represents a (bounded) range of possible sets of values.

In the same way that :ref:`Any` does not represent "the set of all Python
objects" but rather "an unknown set of objects", ``tuple[int, Any]`` does not
represent "the set of all length-two tuples whose first element is an integer".
That is a fully static type, spelled ``tuple[int, object]``.  By contrast,
``tuple[int, Any]`` represents some unknown set of tuple values; it might be
the set of all tuples of two integers, or the set of all tuples of an integer
and a string, or some other set of tuple values.

In practice, this difference is seen (for example) in the fact that we can
assign an expression of type ``tuple[int, Any]`` to a target typed as
``tuple[int, int]``, whereas assigning ``tuple[int, object]`` to ``tuple[int,
int]`` is a static type error. (Again, we formalize this distinction in the
below definitions of materialization and assignability.)

In the same way that the fully static type ``object`` is the upper bound for
the possible sets of values represented by :ref:`Any`, the fully static type
``tuple[int, object]`` is the upper bound for the possible sets of values
represented by ``tuple[int, Any]``.

The gradual guarantee
~~~~~~~~~~~~~~~~~~~~~

:ref:`Any` allows gradually adding static types to a dynamically typed program.
In a fully dynamically typed program, a static checker assigns the type
:ref:`!Any` to all expressions, and should emit no errors. Inferring static
types or adding type annotations to the program (making the program more
statically typed) may result in static type errors, if the program is not
correct or if the static types aren't able to fully represent the runtime
types. Removing type annotations (making the program more dynamic) should not
result in additional static type errors. This is often referred to as the
**gradual guarantee**.

In Python's type system, we don't take the gradual guarantee as a strict
requirement, but it's a useful guideline.

Subtype, supertype, and type equivalence
----------------------------------------

A fully static type ``B`` is a **subtype** of another fully static type ``A``
if and only if the set of values represented by ``B`` is a subset of the set of
values represented by ``A``. Because the subset relation on sets is transitive
and reflexive, the subtype relation is also transitive (if ``C`` is a subtype
of ``B`` and ``B`` is a subtype of ``A``, then ``C`` is a subtype of ``A``) and
reflexive (``A`` is always a subtype of ``A``).

The **supertype** relation is the inverse of subtype: ``A`` is a supertype of
``B`` if and only if ``B`` is a subtype of ``A``; or equivalently, if and only
if the set of values represented by ``A`` is a superset of the values
represented by ``B``. The supertype relation is also transitive and reflexive.

We also define an **equivalence** relation on fully static types: the types
``A`` and ``B`` are equivalent (or "the same type") if and only if ``A`` is a
subtype of ``B`` and ``B`` is a subtype of ``A``. This means that the set of
values represented by ``A`` is both a superset and a subset of the values
represented by ``B``, meaning ``A`` and ``B`` must represent the same set of
values.

We may describe a type ``B`` as "narrower" than a type ``A`` (or as a "proper
subtype" of ``A``) if ``B`` is a subtype of ``A`` and ``B`` is not equivalent
to ``A``. In the same scenario we can describe the type ``A`` as "wider" than
``B``, or a "proper supertype" of ``B``.

Nominal and structural types
----------------------------

For a type such as ``str`` (or any other class), which describes the set of
values whose ``__class__`` is ``str`` or a direct or indirect subclass of it,
subtyping corresponds directly to subclassing. A subclass ``MyStr`` of ``str``
is a subtype of ``str``, because ``MyStr`` represents a subset of the values
represented by ``str``. Such types can be called "nominal types" and this is
"nominal subtyping."

Other types (e.g. :ref:`Protocols` and :ref:`TypedDict`) instead describe a set
of values by the types of their attributes and methods, or the types of their
dictionary keys and values. These are called "structural types". A structural
type may be a subtype of another type without any inheritance or subclassing
relationship, simply because it meets all the requirements of the supertype,
and perhaps adds more, thus representing a subset of the possible values of the
supertype. This is "structural subtyping".

Although the means of specifying the set of values represented by the types
differs, the fundamental concepts are the same for both nominal and structural
types: a type represents a set of possible values and a subtype represents a
subset of those values.

Materialization
---------------

Since :ref:`Any` represents an unknown static type, it does not represent any
known single set of values (it represents an unknown set of values). Thus it is
not in the domain of the subtype, supertype, or equivalence relations on static
types described above.

To relate gradual types more generally, we define a **materialization**
relation. Materialization transforms a "more dynamic" type to a "more static"
type. Given a gradual type ``A``, if we replace zero or more occurrences of
``Any`` in ``A`` with some type (which can be different for each occurrence of
``Any``), the resulting gradual type ``B`` is a materialization of ``A``. (We
can also materialize a :ref:`Callable` type by replacing ``...`` with any type
signature, and materialize ``tuple[Any, ...]`` by replacing it with a
determinate-length tuple type.)

For instance, ``tuple[int, str]`` (a fully static type) and ``tuple[Any, str]``
(a gradual type) are both materializations of ``tuple[Any, Any]``. ``tuple[int,
str]`` is also a materialization of ``tuple[Any, str]``.

If ``B`` is a materialization of ``A``, we can say that ``B`` is a "more
static" type than ``A``, and ``A`` is a "more dynamic" type than ``B``.

The materialization relation is both transitive and reflexive, so it defines a
preorder on gradual types.

.. _`consistent`:

Consistency
-----------

We define a **consistency** relation on gradual types, based on
materialization.

A fully static type ``A`` is consistent with another fully static type ``B`` if
and only if they are the same type (``A`` is equivalent to ``B``).

A gradual type ``A`` is consistent with a gradual type ``B``, and ``B`` is
consistent with ``A``, if and only if there exists some fully static type ``C``
which is a materialization of both ``A`` and ``B``.

:ref:`Any` is consistent with every type, and every type is consistent with
:ref:`!Any`. (This follows from the definitions of materialization and
consistency but is worth stating explicitly.)

The consistency relation is not transitive. ``tuple[int, int]`` is consistent
with ``tuple[Any, int]``, and ``tuple[Any, int]`` is consistent with
``tuple[str, int]``, but ``tuple[int, int]`` is not consistent with
``tuple[str, int]``.

The consistency relation is symmetric. If ``A`` is consistent with ``B``, ``B``
is also consistent with ``A``. It is also reflexive: ``A`` is always consistent
with ``A``.

.. _`assignable`:

The assignable-to (or consistent subtyping) relation
----------------------------------------------------

Given the materialization relation and the subtyping relation, we can define
the **consistent subtype** relation over all types. A type ``B`` is a
consistent subtype of a type ``A`` if there exists a materialization ``A'`` of
``A`` and a materialization ``B'`` of ``B``, where ``A'`` and ``B'`` are both
fully static types, and ``B'`` is a subtype of ``A'``.

Consistent subtyping defines "assignability" for Python.  An expression can be
assigned to a variable (including passed as an argument or returned from a
function) if its type is a consistent subtype of the variable's type annotation
(respectively, parameter's type annotation or return type annotation).

We can say that a type ``B`` is "assignable to" a type ``A`` if ``B`` is a
consistent subtype of ``A``. In this case we can also say that ``A`` is
"assignable from" ``B``.

In the remainder of this specification, we will usually prefer the term
**assignable to** over "consistent subtype of". The two are synonymous, but
"assignable to" is shorter, and may communicate a clearer intuition to many
readers.

For example, ``Any`` is :term:`assignable` to ``int``, because ``int`` is a
materialization of ``Any``, and ``int`` is a subtype of ``int``. The same
materialization also shows that ``int`` is assignable to ``Any``.

The assignable-to relation is not generally symmetric, however. If ``B`` is a
subtype of ``A``, then ``tuple[Any, B]`` is assignable to ``tuple[int, A]``,
because ``tuple[Any, B]`` can materialize to ``tuple[int, B]``, which is a
subtype of ``tuple[int, A]``. But ``tuple[int, A]`` is not assignable to
``tuple[Any, B]``.

For a gradual structural type, consistency and assignability are also
structural. For example, the structural type "all objects with an attribute
``x`` of type ``Any``" is consistent with (and assignable to) the structural
type "all objects with an attribute ``x`` of type ``int``".

Summary of type relations
-------------------------

The subtype, supertype, and equivalence relations establish a partial order on
fully static types. The analogous relations on gradual types (via
materialization) are "assignable-to" (or "consistent subtype"),
"assignable-from" (or "consistent supertype"), and "consistent with". We can
visualize this analogy in the following table:

.. list-table::
   :header-rows: 1

   * - Fully static types
     - Gradual types
   * - ``B`` is a :term:`subtype` of ``A``
     - ``B`` is :term:`assignable` to (or a consistent subtype of) ``A``
   * - ``A`` is a :term:`supertype` of ``B``
     - ``A`` is assignable from (or a consistent supertype of) ``B``
   * - ``B`` is :term:`equivalent` to ``A``
     - ``B`` is :term:`consistent` with ``A``

We can also define an **equivalence** relation on gradual types: the gradual
types ``A`` and ``B`` are equivalent (that is, the same gradual type, not
merely consistent with one another) if and only if all materializations of
``A`` are also materializations of ``B``, and all materializations of ``B``
are also materializations of ``A``.

Attributes and methods
----------------------

In Python, we can do more with objects at runtime than just assign them to
names, pass them to functions, or return them from functions. We can also
get/set attributes and call methods.

In the Python data model, the operations that can be performed on a value all
desugar to method calls. For example, ``a + b`` is (roughly, eliding some
details) syntactic sugar for either ``type(a).__add__(a, b)`` or
``type(b).__radd__(b, a)``.

For a static type checker, accessing ``a.foo`` is a type error unless all
possible objects in the set represented by the type of ``a`` have the ``foo``
attribute. (We consider an implementation of ``__getattr__`` to be a getter for
all attribute names, and similarly for ``__setattr__`` and ``__delattr__``.
There are more `complexities
<https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access>`_;
a full specification of attribute access belongs in its own chapter.)

If all objects in the set represented by the fully static type ``A`` have a
``foo`` attribute, we can say that the type ``A`` has the ``foo`` attribute.

If the type ``A`` of ``a`` in ``a.foo`` is a gradual type, it may not represent
a single set of objects. In this case, ``a.foo`` is a type error if and only if
there does not exist any materialization of ``A`` which has the ``foo``
attribute.

Equivalently, ``a.foo`` is a type error unless the type of ``a`` is assignable
to a type that has the ``foo`` attribute.


.. _`union-types`:

Union types
-----------

Since accepting a small, limited set of expected types for a single
argument is common, the type system supports union types, created with the
``|`` operator.
Example::

  def handle_employees(e: Employee | Sequence[Employee]) -> None:
      if isinstance(e, Employee):
          e = [e]
      ...

A fully static union type ``T1 | T2``, where ``T1`` and ``T2`` are fully static
types, represents the set of values formed by the union of the sets of values
represented by ``T1`` and ``T2``, respectively. Thus, by the definition of the
supertype relation, the union ``T1 | T2`` is a supertype of both ``T1`` and
``T2``, and ``T1`` and ``T2`` are both subtypes of ``T1 | T2``.

A gradual union type ``S1 | S2``, where ``S1`` and ``S2`` are gradual types,
represents all possible sets of values that could be formed by union of the
possible sets of values represented by materializations of ``S1`` and ``S2``,
respectively.

For any materialization of ``S1`` to ``T1`` and ``S2`` to ``T2``, ``S1 | S2``
can likewise be materialized to ``T1 | T2``. Thus, the gradual types ``S1`` and
``S2`` are both assignable to the gradual union type ``S1 | S2``.

If ``B`` is a subtype of ``A``, ``B | A`` is equivalent to ``A``.

This rule applies only to subtypes, not assignable-to. For any type ``T``
(other than the top and bottom types ``object`` and ``Never``), the union ``T | Any`` is
not reducible to a simpler form. It represents an unknown static type with
lower bound ``T``. That is, it represents an unknown set of objects which may
be as large as ``object``, or as small as ``T``, but no smaller.
The exceptions are ``object`` and ``Never``. The union ``object | Any`` is equivalent to
``object``, because ``object`` is a type containing all values and therefore the ``Any``
cannot add any values. Similarly, ``Never | Any`` is equivalent to ``Any``, because
``Never`` is a type containing no values, so that including it in a union cannot add any
values to the type.

Equivalent gradual types can, however, be simplified from unions; e.g.
``list[Any] | list[Any]`` is equivalent to ``list[Any]``. Similarly, the union
``Any | Any`` can be simplified to ``Any``: the union of two unknown sets of
objects is an unknown set of objects.

Union with None
~~~~~~~~~~~~~~~

One common case of union types are *optional* types, which are unions with
``None``. Example::

  def handle_employee(e: Employee | None) -> None: ...

Either the type ``Employee`` or the type of ``None`` are assignable to the
union ``Employee | None``.

A past version of this specification allowed type checkers to assume an optional
type when the default value is ``None``, as in this code::

  def handle_employee(e: Employee = None): ...

This would have been treated as equivalent to::

  def handle_employee(e: Employee | None = None) -> None: ...

This is no longer the recommended behavior. Type checkers should move
towards requiring the optional type to be made explicit.

Support for singleton types in unions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A singleton instance is frequently used to mark some special condition,
in particular in situations where ``None`` is also a valid value
for a variable. Example::

  _empty = object()

  def func(x=_empty):
      if x is _empty:  # default argument value
          return 0
      elif x is None:  # argument was provided and it's None
          return 1
      else:
          return x * 2

To allow precise typing in such situations, the user should use
a union type in conjunction with the ``enum.Enum`` class provided
by the standard library, so that type errors can be caught statically::

  from enum import Enum

  class Empty(Enum):
      token = 0
  _empty = Empty.token

  def func(x: int | None | Empty = _empty) -> int:

      boom = x * 42  # This fails type check

      if x is _empty:
          return 0
      elif x is None:
          return 1
      else:  # At this point typechecker knows that x can only have type int
          return x * 2

Since the subclasses of ``Enum`` cannot be further subclassed,
the type of variable ``x`` can be statically inferred in all branches
of the above example. The same approach is applicable if more than one
singleton object is needed: one can use an enumeration that has more than
one value::

  class Reason(Enum):
      timeout = 1
      error = 2

  def process(response: str | Reason = '') -> str:
      if response is Reason.timeout:
          return 'TIMEOUT'
      elif response is Reason.error:
          return 'ERROR'
      else:
          # response can be only str, all other possible values exhausted
          return 'PROCESSED: ' + response

References
----------

The concepts presented here are derived from the research literature in gradual
typing. See e.g.:

* `Giuseppe Castagna, Victor Lanvin, Tommaso Petrucciani, and Jeremy G. Siek. 2019. Gradual Typing: A New Perspective. <https://doi.org/10.1145/3290329>`_ Proc. ACM Program. Lang. 3, POPL, Article 16 (January 2019), 112 pages
* `Victor Lanvin. A semantic foundation for gradual set-theoretic types. <https://theses.hal.science/tel-03853222/file/va_Lanvin_Victor.pdf>`_ Computer science. Université Paris Cité, 2021. English. NNT : 2021UNIP7159. tel-03853222
