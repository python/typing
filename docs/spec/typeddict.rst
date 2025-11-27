.. _`typeddict`:
.. _`typed-dictionaries`:

Typed dictionaries
==================

(Originally specified in :pep:`589`, with later additions: ``Required``
and ``NotRequired`` in :pep:`655`, use with ``Unpack`` in :pep:`692`,
``ReadOnly`` in :pep:`705`, and ``closed=True`` and ``extra_items=`` in :pep:`728`.)

A TypedDict type represents ``dict`` objects that contain only keys of
type ``str``. There are restrictions on which string keys are valid, and
which values can be associated with each key. Values that :term:`inhabit` a
TypedDict type must be instances of ``dict`` itself, not a subclass.

TypedDict types can define any number of :term:`items <item>`, which are string
keys associated with values of a specified type. For example,
a TypedDict may contain the item ``a: str``, indicating that the key ``a``
must map to a value of type ``str``. Items may be either :term:`required`,
meaning they must be present in every instance of the TypedDict type, or
:term:`non-required`, meaning they may be omitted, but if they are present,
they must be of the type specified in the TypedDict definition. By default,
all items in a TypedDict are mutable, but items
may also be marked as :term:`read-only`, indicating that they may not be
modified.

In addition to explicitly specified items, TypedDicts may allow additional
items. By default, TypedDicts are :term:`open`, meaning they may contain an
unknown set of additional items. They may also be marked as :term:`closed`,
in which case they may not contain any keys beyond those explicitly specified.
As a third option, they may be defined with :term:`extra items` of a specific type.
In this case, there may be any number of additional items present at runtime, but
their values must be of the specified type. Extra items may or may not be
:term:`read-only`. Thus, a TypedDict may be open, closed, or have extra items;
we refer to this property as the *openness* of the TypedDict. For many purposes,
an open TypedDict is equivalent to a TypedDict with read-only extra items of
type ``object``, but certain behaviors differ; for example, the
:ref:`TypedDict constructor <typeddict-constructor>` of open TypedDicts does not
allow unrecognized keys.

A TypedDict is a :term:`structural` type: independent TypedDict types may be
:term:`assignable` to each other based on their structure, even if they do not
share a common base class. For example, two TypedDict types that contain the same
items are :term:`equivalent`. Nevertheless, TypedDict types may inherit from other
TypedDict types to share common items. TypedDict types may also be generic.

Syntax
------

This section outlines the syntax for creating TypedDict types. There are two
syntaxes: the class-based syntax and the functional syntax.

.. _typeddict-class-based-syntax:

Class-based Syntax
^^^^^^^^^^^^^^^^^^

A TypedDict type can be defined using the class definition syntax with
``typing.TypedDict`` as a direct or indirect base class::

    from typing import TypedDict

    class Movie(TypedDict):
        name: str
        year: int

``Movie`` is a TypedDict type with two items: ``'name'`` (with type
``str``) and ``'year'`` (with type ``int``).

A TypedDict can also be created through inheritance from one or more
other TypedDict types::

    class BookBasedMovie(Movie):
        based_on: str

This creates a TypedDict type ``BookBasedMovie`` with three items:
``'name'`` (type ``str``), ``'year'`` (type ``int``), and ``'based_on'`` (type ``str``).
See :ref:`Inheritance <typeddict-inheritance>` for more details.

A generic TypedDict can be created by inheriting from ``Generic`` with a list
of type parameters::

    from typing import Generic, TypeVar

    T = TypeVar('T')

    class Response(TypedDict, Generic[T]):
        status: int
        payload: T

Or, in Python 3.12 and newer, by using the native syntax for generic classes::

    from typing import TypedDict

    class Response[T](TypedDict):
        status: int
        payload: T

It is invalid to specify a base class other than ``TypedDict``, ``Generic``,
or another TypedDict type in a class-based TypedDict definition.
It is also invalid to specify a custom metaclass.

A TypedDict definition may also contain the following keyword arguments
in the class definition:

* ``total``: a boolean literal (``True`` or ``False``) indicating whether
  all items are :term:`required` (``True``, the default) or :term:`non-required`
  (``False``). This affects only items defined in this class, not in any
  base classes, and it does not affect any items that use an explicit
  ``Required[]`` or ``NotRequired[]`` qualifier. The value must be exactly
  ``True`` or ``False``; other expressions are not allowed.
* ``closed``: a boolean literal (``True`` or ``False``) indicating whether
  the TypedDict is :term:`closed` (``True``) or :term:`open` (``False``).
  The latter is the default, except when inheriting from another TypedDict that
  is not open (see :ref:`typeddict-inheritance`), or when the ``extra_items``
  argument is also used.
  As with ``total``, the value must be exactly ``True`` or ``False``. It is an error
  to use this argument together with ``extra_items=``.
* ``extra_items``: indicates that the TypedDict has :term:`extra items`. The argument
  must be a :term:`annotation expression` specifying the type of the extra items.
  The :term:`type qualifier` ``ReadOnly[]`` may be used to indicate that the extra items are
  :term:`read-only`. Other type qualifiers are not allowed. If the extra items type
  is ``Never``, no extra items are allowed, so this is equivalent to ``closed=True``.

The body of the class definition defines the :term:`items <item>` of the TypedDict type.
It may also contain a docstring or ``pass`` statements (primarily to allow the creation of
an empty TypedDict). No other statements are allowed, and type checkers should report an
error if any are present. Type comments are not supported for creating TypedDict items.

.. _`required-notrequired`:
.. _`required`:
.. _`notrequired`:

An item definition takes the form of an attribute annotation, ``key: T``. ``key`` is
an identifier and corresponds to the string key of the item, and ``T`` is an
:term:`annotation expression` specifying the type of the item value. This annotation
expression contains a :term:`type expression`, optionally qualified with one of the
:term:`type qualifiers <type qualifier>` ``Required``, ``NotRequired``, or ``ReadOnly``.
These type qualifiers may be nested arbitrarily or wrapped in ``Annotated[]``. It is
an error to use both ``Required`` and ``NotRequired`` in the same item definition.
An item is :term:`read-only` if and only if the ``ReadOnly`` qualifier is used.

To determine whether an item is :term:`required` or :term:`non-required`, the following
procedure is used:

* If the ``Required`` qualifier is present, the item is required.
* If the ``NotRequired`` qualifier is present, the item is non-required.
* If the ``total`` argument of the TypedDict definition is ``False``, the item is non-required.
* Else, the item is required.

It is valid to use ``Required[]`` and ``NotRequired[]`` even for
items where it is redundant, to enable additional explicitness if desired.
Note that the value of ``total`` only affects items defined in the current class body,
not in any base classes. Thus, inheritance can be used to create a TypedDict that mixes
required and non-required items without using ``Required[]`` or ``NotRequired[]``.

The following example demonstrates some of these rules::

    from typing import TypedDict, NotRequired, Required, ReadOnly, Annotated

    class Movie(TypedDict):
        name: str  # required, not read-only
        year: int  # required, not read-only
        director: NotRequired[str]  # non-required, not read-only
        rating: NotRequired[ReadOnly[float]]  # non-required, read-only
        invalid: Required[NotRequired[int]]  # type checker error: both Required and NotRequired used

    class PartialMovie(TypedDict, total=False):
        name: str  # non-required, not read-only
        year: Required[int]  # required, not read-only
        score: ReadOnly[float]  # non-required, read-only

.. _typeddict-functional-syntax:

Functional syntax
^^^^^^^^^^^^^^^^^

In addition to the class-based syntax, TypedDict types can be created
using an alternative functional syntax. This syntax allows defining
items with keys that are not valid Python identifiers, and it is compatible
with older Python versions such as 3.5 and 2.7 that don't support the
variable definition syntax introduced in :pep:`526`. On the other hand, this syntax
does not support inheritance.

The functional syntax resembles the traditional syntax for defining named tuples::

    from typing import TypedDict

    Movie = TypedDict('Movie', {'name': str, 'year': int})

The syntax comprises a call to ``TypedDict()``, the result of which must be immediately
assigned to a variable with the same name as the first argument to ``TypedDict()``.

The call to ``TypedDict()`` must have two positional arguments. The first is a string
literal specifying the name of the TypedDict type. The second is a dictionary specifying
the :term:`items <item>` of the TypedDict. It must be a dictionary display expression,
not a variable or other expression that evaluates to a dictionary at runtime.
The keys of the dictionary must be string literals and the values must be
:term:`annotation expressions <annotation expression>` following the same rules as
the class-based syntax (i.e., the qualifiers ``Required``, ``NotRequired``, and
``ReadOnly`` are allowed). In addition to the two positional arguments, ``total``,
``closed``, and ``extra_items`` keyword arguments are also supported, with the same
semantics as in the class-based syntax.

Using TypedDict Types
---------------------

Here is an example of how the type ``Movie`` can be used::

    movie: Movie = {'name': 'Blade Runner',
                    'year': 1982}

An explicit ``Movie`` type annotation is generally needed, as
otherwise an ordinary dictionary type could be assumed by a type
checker, for backwards compatibility.  When a type checker can infer
that a constructed dictionary object should be a TypedDict, an
explicit annotation can be omitted.  A typical example is a dictionary
object as a function argument.  In this example, a type checker is
expected to infer that the dictionary argument should be understood as
a TypedDict::

    def record_movie(movie: Movie) -> None: ...

    record_movie({'name': 'Blade Runner', 'year': 1982})

Another example where a type checker should treat a dictionary display
as a TypedDict is in an assignment to a variable with a previously
declared TypedDict type::

    movie: Movie
    ...
    movie = {'name': 'Blade Runner', 'year': 1982}

Operations on ``movie`` can be checked by a static type checker::

    movie['director'] = 'Ridley Scott'  # Error: invalid key 'director'
    movie['year'] = '1982'  # Error: invalid value type ("int" expected)

The code below should be rejected, since ``'title'`` is not a valid
key, and the ``'name'`` key is missing::

    movie2: Movie = {'title': 'Blade Runner',
                     'year': 1982}

The created TypedDict type object is not a real class object.  Here
are the only uses of the type a type checker is expected to allow:

* It can be used in :term:`type expressions <type expression>` to
  represent the TypedDict type.

* It can be used as a callable object with keyword arguments
  corresponding to the TypedDict items; see :ref:`typeddict-constructor`.

* It can be used as a base class, but only when defining a derived
  TypedDict (see :ref:`above <typeddict-class-based-syntax>`).

In particular, TypedDict type objects cannot be used in
``isinstance()`` tests such as ``isinstance(d, Movie)``. This is
consistent with how ``isinstance()`` is not supported for
other type forms such as ``list[str]``.

.. _typeddict-constructor:

The TypedDict constructor
^^^^^^^^^^^^^^^^^^^^^^^^^

TypedDict types are callable at runtime and can be used as a constructor
to create values that conform to the TypedDict type. The constructor
takes only keyword arguments, corresponding to the items of the TypedDict.
Example::

    m = Movie(name='Blade Runner', year=1982)

When called, the TypedDict type object returns an ordinary
dictionary object at runtime::

    print(type(m))  # <class 'dict'>

Every :term:`required` item must be provided as a keyword argument. :term:`Non-required`
items may be omitted. Whether an item is read-only has no effect on the
constructor.

Closed and open TypedDicts allow no additional items beyond those explicitly
defined, but TypedDicts with extra items allow arbitrary keyword arguments,
which must be of the specified type. Example::

    from typing import TypedDict, ReadOnly

    class MovieWithExtras(TypedDict, extra_items=ReadOnly[int | str]):
        name: str
        year: int

    m1 = MovieWithExtras(name='Blade Runner', year=1982)  # OK
    m2 = MovieWithExtras(name='The Godfather', year=1972, director='Francis Ford Coppola', rating=9)  # OK
    m3 = MovieWithExtras(name='Inception', year=2010, budget=160.0)  # Type check error: budget must be int or str

Initialization from dictionary literals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type checkers should also allow initializing a value of TypedDict type from
a dictionary literal::

    m: Movie = {'name': 'Blade Runner', 'year': 1982}  # OK

Or from a call to ``dict()`` with keyword arguments::

    m: Movie = dict(name='Blade Runner', year=1982)  # OK

In these cases, extra keys should not be allowed unless the TypedDict
is defined to allow :term:`extra items`. In this example, the ``director`` key is not defined in
``Movie`` and is expected to generate an error from a type checker::

    m: Movie = dict(
        name='Alien',
        year=1979,
        director='Ridley Scott')  # error: Unexpected key 'director'

If a TypedDict has extra items, extra keys are allowed, provided their value
matches the extra items type::

    class ExtraMovie(TypedDict, extra_items=bool):
        name: str

    a: ExtraMovie = {"name": "Blade Runner", "novel_adaptation": True}  # OK
    b: ExtraMovie = {
        "name": "Blade Runner",
        "year": 1982,  # Not OK. 'int' is not assignable to 'bool'
    }

Here, ``extra_items=bool`` specifies that items other than ``'name'``
have a value type of ``bool`` and are non-required.

.. _typeddict-inheritance:

Inheritance
-----------

As discussed under :ref:`typeddict-class-based-syntax`, TypedDict types
can inherit from one or more other TypedDict types.  In this case the
``TypedDict`` base class should not be included.  Example::

    class BookBasedMovie(Movie):
        based_on: str

Now ``BookBasedMovie`` has keys ``name``, ``year``, and ``based_on``. It is
equivalent to this definition, since TypedDict types are :term:`structural` types::

    class BookBasedMovie(TypedDict):
        name: str
        year: int
        based_on: str

Overriding items
^^^^^^^^^^^^^^^^

Under limited circumstances, subclasses may redeclare items defined in a superclass with
a different type or different qualifiers. Redeclaring an item with the same type and qualifiers
is always allowed, although it is redundant.

If an item is mutable in a superclass, it must remain mutable in the subclass. Similarly,
mutable items that are :term:`required` in a superclass must remain required in the subclass,
and mutable :term:`non-required` items in the superclass must remain non-required in the subclass.
However, if the superclass item is :term:`read-only`, a superclass item that is non-required
may be overridden with a required item in the subclass. A read-only item in a superclass
may be redeclared as mutable (that is, without the ``ReadOnly`` qualifier) in a subclass.
These rules are necessary for type safety.

If an item is read-only in the superclass, the subclass may redeclare it with a different type
that is :term:`assignable` to the superclass type. Otherwise, changing the type of an item is not allowed.
Example::

   class X(TypedDict):
       x: str
       y: ReadOnly[int]
       z: int

   class Y(X):
       x: int  # Type check error: cannot overwrite TypedDict field "x"
       y: bool  # OK: bool is assignable to int, and a mutable item can override a read-only one
       z: bool  # Type check error: key is mutable, so subclass type must be consistent with superclass

Openness
^^^^^^^^

The openness of a TypedDict (whether it is :term:`open`, :term:`closed`, or has :term:`extra items`)
is inherited from its superclass by default::

    class ClosedBase(TypedDict, closed=True):
        name: str

    class ClosedChild(ClosedBase):  # also closed
        pass

    class ExtraItemsBase(TypedDict, extra_items=int | None):
        name: str

    class ExtraItemsChild(ExtraItemsBase):  # also has extra_items=int | None
        pass

However, subclasses may also explicitly use the ``closed`` and ``extra_items`` arguments
to change the openness of the TypedDict, but in some cases this yields a type checker error:

- If the base class is open, all possible states are allowed in the subclass: it may remain open,
  it may be closed (with ``closed=True``), or it may have extra items (with ``extra_items=...``).

- If the base class is closed, any child classes must also be closed.

- If the base class has extra items, but they are not read-only, the child class must also allow
  the same extra items.

- If the base class has read-only extra items, the child class may be closed,
  or it may redeclare its extra items with a type that is :term:`assignable` to the base class type.
  Child classes may also have mutable extra items if the base class has read-only extra items.

For example::

    class ExtraItemsRO(TypedDict, extra_items=ReadOnly[int | str]):
        name: str

    class ClosedChild(ExtraItemsRO, closed=True):  # OK
        pass

    # OK, str is assignable to int | str, and mutable extra items can override read-only ones
    class NarrowerChild(ExtraItemsRO, extra_items=str):
        pass

When a TypedDict has extra items, this effectively defines the value type of any unnamed
items accepted to the TypedDict and marks them as non-required. Thus, there are some
restrictions on the items that can be added in subclasses. For each item
added in a subclass of a class with extra items of type ``T``, the following rules must be followed:

- If ``extra_items`` is read-only

  - The item can be either required or non-required
  - The item's value type must be :term:`assignable` to ``T``

- If ``extra_items`` is not read-only

  - The item must be non-required
  - The item's value type must be :term:`consistent` with ``T``

For example::

    class MovieBase(TypedDict, extra_items=int | None):
        name: str

    class MovieRequiredYear(MovieBase):  # Not OK. Required key 'year' is not known to 'MovieBase'
        year: int | None

    class MovieNotRequiredYear(MovieBase):  # Not OK. 'int | None' is not consistent with 'int'
        year: NotRequired[int]

    class MovieWithYear(MovieBase):  # OK
        year: NotRequired[int | None]

    class BookBase(TypedDict, extra_items=ReadOnly[int | str]):
        title: str

    class Book(BookBase, extra_items=str):  # OK
        year: int  # OK, since extra_items is read-only

Multiple inheritance
^^^^^^^^^^^^^^^^^^^^

TypedDict types may use multiple inheritance to inherit items from multiple
base classes. Here is an example::

    class X(TypedDict):
        x: int

    class Y(TypedDict):
        y: str

    class XYZ(X, Y):
        z: bool

The TypedDict ``XYZ`` has three items: ``x`` (type ``int``), ``y``
(type ``str``), and ``z`` (type ``bool``).

Multiple inheritance does not allow conflicting types for the same item::

   class X(TypedDict):
      x: int

   class Y(TypedDict):
      x: str

   class XYZ(X, Y):  # Type check error: cannot overwrite TypedDict field "x" while merging
      xyz: bool

.. _typeddict-assignability:

Subtyping and assignability
---------------------------

Because TypedDict types are :term:`structural` types, a TypedDict ``T1`` is :term:`assignable` to another
TypedDict type ``T2`` if the two are structurally compatible, meaning that all operations that
are allowed on ``T2`` are also allowed on ``T1``. For similar reasons, TypedDict types are
generally not assignable to any specialization of ``dict`` or ``Mapping``, other than ``Mapping[str, object]``,
though certain :term:`closed` TypedDicts and TypedDicts with :term:`extra items` may be assignable
to these types.

The rest of this section discusses the :term:`subtyping <subtype>` rules for TypedDict in more detail.
As with any type, the rules for :term:`assignability <assignable>` can be derived from the subtyping
rules using the :term:`materialization <materialize>` procedure. Generally, this means that where
":term:`equivalent`" is mentioned below, the :term:`consistency <consistent>` relation can be used instead
when implementing assignability, and where ":term:`subtyping <subtype>`" between elements of a
TypedDict is mentioned, assignability can be used instead when implementing assignability between TypedDicts.

Subtyping between TypedDict types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A TypedDict type ``B`` is a :term:`subtype` of a TypedDict type ``A`` if
and only if all of the conditions below are satisfied. For the purposes of these conditions,
an :term:`open` TypedDict is treated as if it had read-only :term:`extra items` of type ``object``.

The conditions are as follows:

- For each item in ``A``:

  - If it is required in ``A``:

    - It must also be required in ``B``.
    - If it is read-only in ``A``, the item type in ``B`` must be a subtype of the item type in ``A``.
      (For :term:`assignability <assignable>` between two TypedDicts, the first item must instead
      be assignable to the second.)

    - If it is mutable in ``A``, it must also be mutable in ``B``, and the item type in ``B`` must be
      :term:`equivalent` to the item type in ``A``. (It follows that for assignability, the two item types
      must be :term:`consistent`.)

  - If it is non-required in ``A``:

    - If it is read-only in ``A``:

      - If ``B`` has an item with the same key, its item type must be a subtype of the item type in ``A``.
      - Else:

        - If ``B`` is closed, the check succeeds.
        - If ``B`` has extra items, the extra items type must be a subtype of the item type in ``A``.

    - If it is mutable in ``A``:

      - If ``B`` has an item with the same key, it must also be mutable and non-required, and its item type must be
        :term:`equivalent` to the item type in ``A``.

      - Else:

        - If ``B`` is closed, the check fails.
        - If ``B`` has extra items, the extra items type must not be read-only and must
          be :term:`equivalent` to the item type in ``A``.

- If ``A`` is closed, ``B`` must also be closed, and it must not contain any items that are not present in ``A``.
- If ``A`` has read-only extra items, ``B`` must either be closed or also have extra items, and the extra items type in ``B``
  must be a subtype of the extra items type in ``A``. Additionally, for any items in ``B`` that are not present in ``A``,
  the item type must be a subtype of the extra items type in ``A``.
- If ``A`` has mutable extra items, ``B`` must also have mutable extra items, and the extra items type in ``B``
  must be :term:`equivalent` to the extra items type in ``A``. Additionally, for any items in ``B`` that are not present in ``A``,
  the item type must be :term:`equivalent` to the extra items type in ``A``.

The intuition behind these rules is that any operation that is valid on ``A`` must also be valid and safe on ``B``.
For example, any key access on ``A`` that is guaranteed to succeed (because the item is required) must also succeed on ``B``,
and any mutating operation (such as setting or deleting a key) that is allowed on ``A`` must also be allowed on ``B``.

An example where mutability is relevant::

    class A(TypedDict):
        x: int | None

    class B(TypedDict):
        x: int

    def f(a: A) -> None:
        a['x'] = None

    b: B = {'x': 0}
    f(b)  # Type check error: 'B' not assignable to 'A'
    b['x'] + 1  # Runtime error: None + 1

.. _typeddict-mapping:

Subtyping with ``Mapping``
^^^^^^^^^^^^^^^^^^^^^^^^^^

A TypedDict type is a :term:`subtype` of a type of the form ``Mapping[str, VT]``
when all value types of the items in the TypedDict
are subtypes of ``VT``. For the purpose of this rule, an :term:`open` TypedDict is considered
to have read-only :term:`extra items` of type ``object``.

For example::

    class MovieExtraStr(TypedDict, extra_items=str):
        name: str

    extra_str: MovieExtraStr = {"name": "Blade Runner", "summary": ""}
    str_mapping: Mapping[str, str] = extra_str  # OK

    class MovieExtraInt(TypedDict, extra_items=int):
        name: str

    extra_int: MovieExtraInt = {"name": "Blade Runner", "year": 1982}
    int_mapping: Mapping[str, int] = extra_int  # Not OK. 'int | str' is not assignable with 'int'
    int_str_mapping: Mapping[str, int | str] = extra_int  # OK

As a consequence, every TypedDict type is :term:`assignable` to ``Mapping[str, object]``.

.. _typeddict-dict:

Subtyping with ``dict``
^^^^^^^^^^^^^^^^^^^^^^^

Generally, TypedDict types are not subtypes of any specialization of ``dict[...]`` type, since
dictionary types allow destructive operations, including ``clear()``. They
also allow arbitrary keys to be set, which would compromise type safety.

However, a TypedDict with :term:`extra items` may be a subtype of ``dict[str, VT]``,
provided certain conditions are met, because it introduces sufficient restrictions
for this subtyping relation to be safe.
A TypedDict type is a subtype of ``dict[str, VT]`` if the following conditions are met:

- The TypedDict type has mutable :term:`extra items` of a type that is :term:`equivalent` to ``VT``.
- All items on the TypedDict satisfy the following conditions:

  - The value type of the item is :term:`equivalent` to ``VT``.
  - The item is not read-only.
  - The item is not required.

For example::

    class IntDict(TypedDict, extra_items=int):
        pass

    class IntDictWithNum(IntDict):
        num: NotRequired[int]

    def f(x: IntDict) -> None:
        v: dict[str, int] = x  # OK
        v.clear()  # OK

    not_required_num_dict: IntDictWithNum = {"num": 1, "bar": 2}
    regular_dict: dict[str, int] = not_required_num_dict  # OK
    f(not_required_num_dict)  # OK

In this case, some methods that are otherwise unavailable on a TypedDict are allowed,
with signatures matching ``dict[str, VT]``
(e.g.: ``__setitem__(self, key: str, value: VT) -> None``)::

    not_required_num_dict.clear()  # OK

    reveal_type(not_required_num_dict.popitem())  # OK. Revealed type is 'tuple[str, int]'

    def f(not_required_num_dict: IntDictWithNum, key: str):
        not_required_num_dict[key] = 42  # OK
        del not_required_num_dict[key]  # OK

On the other hand, ``dict[str, VT]`` is not assignable to any TypedDict type,
because such a type includes instances of subclasses of ``dict``::

    class CustomDict(dict[str, int]):
        pass

    def f(might_not_be_a_builtin_dict: dict[str, int]):
        int_dict: IntDict = might_not_be_a_builtin_dict # Not OK

    not_a_builtin_dict = CustomDict({"num": 1})
    f(not_a_builtin_dict)

.. _typeddict-operations:

Supported and Unsupported Operations
------------------------------------

Type checkers should support restricted forms of most ``dict``
operations on TypedDict objects.  The guiding principle is that
operations not involving ``Any`` types should be rejected by type
checkers if they may violate runtime type safety.  Here are some of
the most important type safety violations to prevent:

1. A required key is missing.

2. A value has an invalid type.

3. A key that is not defined in the TypedDict type is added.

4. Read-only items are modified or deleted.

.. _`readonly`:

Items that are :term:`read-only` may not be mutated (added, modified, or removed)::

    from typing import ReadOnly

    class Band(TypedDict):
        name: str
        members: ReadOnly[list[str]]

    blur: Band = {"name": "blur", "members": []}
    blur["name"] = "Blur"  # OK: "name" is not read-only
    blur["members"] = ["Damon Albarn"]  # Type check error: "members" is read-only
    blur["members"].append("Damon Albarn")  # OK: list is mutable

The exact type checking rules are up to each type checker to decide.
In some cases potentially unsafe operations may be accepted if the
alternative is to generate false positive errors for idiomatic code.
Sometimes, operations on :term:`closed` TypedDicts or TypedDicts with
:term:`extra items` are safe even if they would be unsafe on
:term:`open` TypedDicts, so type checker behavior may depend on the
openness of the TypedDict.

Allowed keys
^^^^^^^^^^^^

Many operations on TypedDict objects involve specifying a dictionary key.
Examples include accessing an item with ``d['key']`` or setting an item with
``d['key'] = value``.

A key that is not a literal should generally be rejected, since its
value is unknown during type checking, and thus can cause some of the
above violations. This involves both destructive operations such as setting
an item and read-only operations such as subscription expressions.

The use of a key that is not known to exist should be reported as an error,
even if this wouldn't necessarily generate a runtime type error.  These are
often mistakes, and these may insert values with an invalid type if
:term:`structural` :term:`assignability <assignable>` hides the types of
certain items. For example, ``d['x'] = 1`` should generate a type check error
if ``'x'`` is not a valid key for ``d`` (which is assumed to be a TypedDict
type), unless ``d`` has mutable :term:`extra items` of a compatible type.

Type checkers should allow :ref:`final names <uppercase-final>` with
string values to be used instead of string literals in operations on
TypedDict objects.  For example, this is valid::

   YEAR: Final = 'year'

   m: Movie = {'name': 'Alien', 'year': 1979}
   years_since_epoch = m[YEAR] - 1970

Similarly, an expression with a suitable :ref:`literal type <literal>`
can be used instead of a literal value::

   def get_value(movie: Movie,
                 key: Literal['year', 'name']) -> int | str:
       return movie[key]

Specific operations
^^^^^^^^^^^^^^^^^^^

This section discusses some specific operations in more detail.

* As an exception to the general rule around non-literal keys, ``d.get(e)`` and ``e in d``
  should be allowed for TypedDict objects, for an arbitrary expression
  ``e`` with type ``str``.  The motivation is that these are safe and
  can be useful for introspecting TypedDict objects.  The static type
  of ``d.get(e)`` should be the union of all possible item types in ``d``
  if the string value of ``e`` cannot be determined statically.
  (This simplifies to ``object`` if ``d`` is :term:`open`.)

* ``clear()`` is not safe on :term:`open` TypedDicts since it could remove required items, some of which
  may not be directly visible because of :term:`structural`
  :term:`assignability <assignable>`. However, this method is safe on
  :term:`closed` TypedDicts and TypedDicts with :term:`extra items` if
  there are no required or read-only items and there cannot be any subclasses with required
  or read-only items.

* ``popitem()`` is similarly unsafe on many TypedDicts, even
  if all known items are :term:`non-required`.

* ``del obj['key']`` should be rejected unless ``'key'`` is a
  non-required, mutable key.

* Type checkers may allow reading an item using ``d['x']`` even if
  the key ``'x'`` is not required, instead of requiring the use of
  ``d.get('x')`` or an explicit ``'x' in d`` check.  The rationale is
  that tracking the existence of keys is difficult to implement in full
  generality, and that disallowing this could require many changes to
  existing code.
  Similarly, type checkers may allow indexed accesses
  with arbitrary str keys when a TypedDict is :term:`closed` or has :term:`extra items`.
  For example::

    def bar(movie: MovieExtraInt, key: str) -> None:
        reveal_type(movie[key])  # Revealed type is 'str | int'

* The return types of the ``items()`` and ``values()`` methods can be determined
  from the union of all item types in the TypedDict (which would include ``object``
  for :term:`open` TypedDicts). Therefore, type checkers should infer more precise
  types for TypedDicts that are not open::

    from typing import TypedDict

    class MovieExtraInt(TypedDict, extra_items=int):
        name: str

    def foo(movie: MovieExtraInt) -> None:
        reveal_type(movie.items())  # Revealed type is 'dict_items[str, str | int]'
        reveal_type(movie.values())  # Revealed type is 'dict_values[str, str | int]'

* The ``update()`` method should not allow mutating a read-only item.
  Therefore, type checkers should error if a
  TypedDict with a read-only item is updated with another TypedDict that declares
  that item::

    class A(TypedDict):
        x: ReadOnly[int]
        y: int

    a1: A = {"x": 1, "y": 2}
    a2: A = {"x": 3, "y": 4}
    a1.update(a2)  # Type check error: "x" is read-only in A

  Unless the declared value is of bottom type (:data:`~typing.Never`)::

    class B(TypedDict):
        x: NotRequired[typing.Never]
        y: ReadOnly[int]

    def update_a(a: A, b: B) -> None:
        a.update(b)  # Accepted by type checker: "x" cannot be set on b

  Note: Nothing will ever match the ``Never`` type, so an item annotated with it must be absent.

Backwards Compatibility
-----------------------

To retain backwards compatibility, type checkers should not infer a
TypedDict type unless it is sufficiently clear that this is desired by
the programmer.  When unsure, an ordinary dictionary type should be
inferred.  Otherwise existing code that type checks without errors may
start generating errors once TypedDict support is added to the type
checker, since TypedDict types are more restrictive than dictionary
types.  In particular, they aren't subtypes of dictionary types.
