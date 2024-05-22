.. _`type-system-concepts`:

Type system concepts
====================

Static, dynamic, and gradual typing
-----------------------------------

A **statically-typed** programming language runs a type-checker before running
a program. The program is required to be well-typed according to the language's
type system. The type system assigns a type to all expressions in the language
and verifies that their uses obey the typing rules. Normally, a program that is
not well-typed (i.e., one that contains a type error) will not run. Java and
C++ are examples of statically-typed object-oriented languages.

A **dynamically-typed** programming language does not run a type-checker before
running a program. Instead, it will check the types of values before performing
operations on them at runtime. This is not to say that the language is
"untyped". Values at runtime have a type and their uses obey typing rules. Not
every operation will be checked, but certain primitive operations in the
language such as attribute access or arithmetic will be.  Python was
historically a dynamically-typed language.

**Gradual typing** is the name for a specific way to combine static and dynamic
typing.  It allows mixing static and dynamic checking at a fine level of
granularity.  For instance, in Python, individual variables, parameters, and
return values can be either statically or dynamically typed.  Data structures
such as objects can have a mix of static and dynamic checking.  As an example,
a Python dictionary could choose to have static checking of the key type but
dynamic checking of the value type.

In gradual typing, a dynamically typed value is indicated by a special
"unknown" or "dynamic" type.  In Python, the unknown type is spelled
:ref:`Any`. It indicates to the static type checker that this value should not
be subject to static checking.  The system should not signal a static type
error for use of an expression with type :ref:`Any`.  Instead, the expression's
value will be dynamically checked, according to the Python runtime's usual
checks on the types of runtime values.

This specification describes a gradual type system for Python.

Static, dynamic, and gradual types
----------------------------------

We will refer to types that do not contain :ref:`Any` as a sub-part as **static
types**. The dynamic type :ref:`Any` is the **dynamic type**. Any type other
than :ref:`Any` that does contain :ref:`Any` as a sub-part is a **gradual
type**.

Static types
~~~~~~~~~~~~

A static type can intuitively be understood as denoting a set of runtime
values. For instance, the Python static type ``object`` is the set of all
Python objects. The Python static type ``bool`` is the set of values ``{ True,
False }``. The Python static type ``str`` is the set of all Python strings;
more precisely, the set of all Python objects whose runtime type (i.e.
``__class__`` attribute) is either ``str`` or a class that inherits ``str``,
including transitively; i.e. a type with ``str`` in its method resolution
order. Static types can also be specified in other ways. For example,
:ref:`Protocols` specify a static type which is the set of all objects which
share a certain set of attributes and/or methods.

The dynamic type
~~~~~~~~~~~~~~~~

The dynamic type :ref:`Any` represents an unknown static type. It denotes some
unknown set of values.

At first glance, this may appear similar to the static type ``object``, which
represents the set of all Python objects. But it is quite different.

If a value has the static type ``object``, a static type checker should ensure
that all operations on the value are valid for all Python objects, or else emit
a static type error. This allows very few operations! For example, if ``x`` is
typed as ``object``, ``x.foo`` should be a static type error, because not all
Python objects have an attribute ``foo``.

A value typed as :ref:`Any`, on the other hand, should be assumed to have
_some_ specific static type, but _which_ static type is not known. A static
checker should not emit any errors that depend on assuming a particular static
type; a static checker should instead assume that the runtime is responsible
for checking the type of operations on this value, as in a dynamically-typed
language.

The subtype relation
--------------------

A static type ``B`` is a **subtype** of another static type ``A`` if (and only
if) the set of values represented by ``B`` is a subset of the set of values
represented by ``A``. Because the subset relation on sets is transitive and
reflexive, the subtype relation is also transitive (if ``A`` is a subtype of
``B`` and ``B`` is a subtype of ``C``, then ``A`` is a subtype of ``C``) and
reflexive (``A`` is always a subtype of ``A``).

The **supertype** relation is the inverse of subtype: ``A`` is a supertype of
``B`` if (and only if) ``B`` is a subtype of ``A``; or equivalently, if (and
only if) the set of values represented by ``A`` is a superset of the values
represented by ``B``. The supertype relation is also transitive and reflexive.

We also define an **equivalence** relation on static types: the types ``A`` and
``B`` are equivalent (or "the same type") if (and only if) ``A`` is a subtype
of ``B`` and ``B`` is a subtype of ``A``. This means that the set of values
represented by ``A`` is both a superset and a subset of the values represented
by ``B``, meaning ``A`` and ``B`` must represent the same set of values.

We may describe a type ``B`` as "narrower" than a type ``A`` if ``B`` is a
subtype of ``A`` and ``B`` is not equivalent to ``A``.

The consistency relation
------------------------

Since :ref:`Any` (the dynamic type) represents an unknown static type, it does
not represent any known single set of values, and thus it is not in the domain
of the subtype, supertype, or equivalence relations on static types described
above.

We define a **materialization** relation from gradual types to gradual and
static types as follows: if replacing one or more occurrences of ``Any`` in
gradual type ``A`` with some gradual or static type results in the gradual or
static type ``B``, then ``B`` is a materialization of ``A``. For instance,
``tuple[int, str]`` (a static type) and ``tuple[Any, str]`` (a gradual type)
are both materializations of ``tuple[Any, Any]``. If ``B`` is a materialization
of ``A``, we can say that ``B`` is a more precise type than ``A``.

We define a **consistency** relation over all types (the dynamic type, gradual
types, and static types.)

A static type ``A`` is consistent with another static type ``B`` only if they
are the same type (``A`` is equivalent to ``B``.)

The dynamic type ``Any`` is consistent with every type, and every type is
consistent with ``Any``.

A gradual type ``C`` is consistent with a gradual or static type ``D``, and
``D`` is consistent with ``C``, if ``D`` is a materialization of ``C``.

The consistency relation is not transitive. ``tuple[int, int]`` and
``tuple[str, int]`` are both consistent with ``tuple[Any, int]]``, but
``tuple[str, int]`` is not consistent with ``tuple[int, int]``.

The consistency relation is symmetric. If ``A`` is consistent with ``B``, ``B``
is also consistent with ``A``. It is also reflexive: ``A`` is always consistent
with ``A``.

The consistent subtype relation
-------------------------------

Given the consistency relation and the subtyping relation, we define the
**consistent subtype** relation over all types. A type ``A`` is a consistent
subtype of a type ``B`` if there exists a materialization ``A'`` of ``A`` and a
materialization ``B'`` of ``B``, where ``A'`` and ``B'`` are both static types,
and ``A'`` is a subtype of ``B'``.

For example, ``Any`` is a consistent subtype of ``int``, because ``int`` is a
materialization of ``Any``, and ``int`` is a subtype of ``int``. The same
materialization also gives that ``int`` is a consistent subtype of ``Any``.

Consistent subtyping defines assignability
------------------------------------------

Consistent subtyping defines "assignability" for Python.  An expression can be
assigned to a variable (including passed as a parameter, and also returned from
a function) if it is a consistent subtype of the variable's type annotation
(respectively, parameter's type annotation or return type annotation).

We can say that a type ``A`` is "assignable to" a type ``B`` if ``A`` is a
consistent subtype of ``B``.

References
----------

The concepts presented here are derived from the research literature in gradual
typing. See::

* `Victor Lanvin. A semantic foundation for gradual set-theoretic types. Computer science. Université Paris Cité, 2021. English. NNT : 2021UNIP7159. tel-03853222 <https://theses.hal.science/tel-03853222/file/va_Lanvin_Victor.pdf>`_
