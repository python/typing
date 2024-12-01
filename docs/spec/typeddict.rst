.. _`typed-dictionaries`:

Typed dictionaries
==================

.. _`typeddict`:

TypedDict
---------

(Originally specified in :pep:`589`.)

A TypedDict type represents dictionary objects with a specific set of
string keys, and with specific value types for each valid key.  Each
string key can be either required (it must be present) or
non-required (it doesn't need to exist).

There are two ways of defining TypedDict types.  The first uses
a class-based syntax.  The second is an alternative
assignment-based syntax that is provided for backwards compatibility,
to allow the feature to be backported to older Python versions.  The
rationale is similar to why :pep:`484` supports a comment-based
annotation syntax for Python 2.7: type hinting is particularly useful
for large existing codebases, and these often need to run on older
Python versions.  The two syntax options parallel the syntax variants
supported by ``typing.NamedTuple``.  Other features include
TypedDict inheritance and totality (specifying whether keys are
required or not).

This section also provides a sketch of how a type checker is expected to
support type checking operations involving TypedDict objects. Similar to
:pep:`484`, this discussion is left somewhat vague on purpose, to allow
experimentation with a wide variety of different type checking approaches. In
particular, :term:`assignability <assignable>` should be :term:`structural`: a
more specific TypedDict type can be assignable to a more general TypedDict
type, without any inheritance relationship between them.

.. _typeddict-class-based-syntax:

Class-based Syntax
^^^^^^^^^^^^^^^^^^

A TypedDict type can be defined using the class definition syntax with
``typing.TypedDict`` as the sole base class::

    from typing import TypedDict

    class Movie(TypedDict):
        name: str
        year: int

``Movie`` is a TypedDict type with two items: ``'name'`` (with type
``str``) and ``'year'`` (with type ``int``).

A type checker should validate that the body of a class-based
TypedDict definition conforms to the following rules:

* The class body should only contain lines with item definitions of the
  form ``key: value_type``, optionally preceded by a docstring.  The
  syntax for item definitions is identical to attribute annotations,
  but there must be no initializer, and the key name actually refers
  to the string value of the key instead of an attribute name.

* Type comments cannot be used with the class-based syntax, for
  consistency with the class-based ``NamedTuple`` syntax.  Instead,
  `Alternative Syntax`_ provides an
  alternative, assignment-based syntax for backwards compatibility.

* String literal forward references are valid in the value types.

* Methods are not allowed, since the runtime type of a TypedDict
  object will always be just ``dict`` (it is never a subclass of
  ``dict``).

* Specifying a metaclass is not allowed.

* TypedDicts may be made generic by adding ``Generic[T]`` among the
  bases (or, in Python 3.12 and higher, by using the new
  syntax for generic classes).

An empty TypedDict can be created by only including ``pass`` in the
body (if there is a docstring, ``pass`` can be omitted)::

    class EmptyDict(TypedDict):
        pass


Using TypedDict Types
^^^^^^^^^^^^^^^^^^^^^

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

* It can be used in type annotations and in any context where an
  arbitrary type hint is valid, such as in type aliases and as the
  target type of a cast.

* It can be used as a callable object with keyword arguments
  corresponding to the TypedDict items.  Non-keyword arguments are not
  allowed.  Example::

      m = Movie(name='Blade Runner', year=1982)

  When called, the TypedDict type object returns an ordinary
  dictionary object at runtime::

      print(type(m))  # <class 'dict'>

* It can be used as a base class, but only when defining a derived
  TypedDict.  This is discussed in more detail below.

In particular, TypedDict type objects cannot be used in
``isinstance()`` tests such as ``isinstance(d, Movie)``. The reason is
that there is no existing support for checking types of dictionary
item values, since ``isinstance()`` does not work with many
types, including common ones like ``list[str]``.  This would be needed
for cases like this::

    class Strings(TypedDict):
        items: list[str]

    print(isinstance({'items': [1]}, Strings))    # Should be False
    print(isinstance({'items': ['x']}, Strings))  # Should be True

The above use case is not supported.  This is consistent with how
``isinstance()`` is not supported for ``list[str]``.


Inheritance
^^^^^^^^^^^

It is possible for a TypedDict type to inherit from one or more
TypedDict types using the class-based syntax.  In this case the
``TypedDict`` base class should not be included.  Example::

    class BookBasedMovie(Movie):
        based_on: str

Now ``BookBasedMovie`` has keys ``name``, ``year``, and ``based_on``. It is
equivalent to this definition, since TypedDict types use :term:`structural`
:term:`assignability <assignable>`::

    class BookBasedMovie(TypedDict):
        name: str
        year: int
        based_on: str

Here is an example of multiple inheritance::

    class X(TypedDict):
        x: int

    class Y(TypedDict):
        y: str

    class XYZ(X, Y):
        z: bool

The TypedDict ``XYZ`` has three items: ``x`` (type ``int``), ``y``
(type ``str``), and ``z`` (type ``bool``).

A TypedDict cannot inherit from both a TypedDict type and a
non-TypedDict base class other than ``Generic``.

Additional notes on TypedDict class inheritance:

* Changing a field type of a parent TypedDict class in a subclass is not allowed.
  Example::

   class X(TypedDict):
      x: str

   class Y(X):
      x: int  # Type check error: cannot overwrite TypedDict field "x"

  In the example outlined above TypedDict class annotations returns
  type ``str`` for key ``x``::

   print(Y.__annotations__)  # {'x': <class 'str'>}


* Multiple inheritance does not allow conflict types for the same name field::

   class X(TypedDict):
      x: int

   class Y(TypedDict):
      x: str

   class XYZ(X, Y):  # Type check error: cannot overwrite TypedDict field "x" while merging
      xyz: bool


Totality
^^^^^^^^

By default, all keys must be present in a TypedDict.  It is possible
to override this by specifying *totality*.  Here is how to do this
using the class-based syntax::

    class Movie(TypedDict, total=False):
        name: str
        year: int

This means that a ``Movie`` TypedDict can have any of the keys omitted. Thus
these are valid::

    m: Movie = {}
    m2: Movie = {'year': 2015}

A type checker is only expected to support a literal ``False`` or
``True`` as the value of the ``total`` argument.  ``True`` is the
default, and makes all items defined in the class body be required.

The totality flag only applies to items defined in the body of the
TypedDict definition.  Inherited items won't be affected, and instead
use totality of the TypedDict type where they were defined.  This makes
it possible to have a combination of required and non-required keys in
a single TypedDict type. Alternatively, ``Required`` and ``NotRequired``
(see below) can be used to mark individual items as required or non-required.

.. _typeddict-functional-syntax:

Alternative Syntax
^^^^^^^^^^^^^^^^^^

This section provides an alternative syntax that can be backported to
older Python versions such as 3.5 and 2.7 that don't support the
variable definition syntax introduced in :pep:`526`.  It
resembles the traditional syntax for defining named tuples::

    Movie = TypedDict('Movie', {'name': str, 'year': int})

It is also possible to specify totality using the alternative syntax::

    Movie = TypedDict('Movie',
                      {'name': str, 'year': int},
                      total=False)

The semantics are equivalent to the class-based syntax.  This syntax
doesn't support inheritance, however.  The
motivation for this is keeping the backwards compatible syntax as
simple as possible while covering the most common use cases.

A type checker is only expected to accept a dictionary display expression
as the second argument to ``TypedDict``.  In particular, a variable that
refers to a dictionary object does not need to be supported, to simplify
implementation.


Assignability
^^^^^^^^^^^^^

First, any TypedDict type is :term:`assignable` to ``Mapping[str, object]``.

Second, a TypedDict type ``B`` is :term:`assignable` to a TypedDict ``A`` if
and only if both of these conditions are satisfied:

* For each key in ``A``, ``B`` has the corresponding key and the corresponding
  value type in ``B`` is :term:`consistent` with the value type in ``A``.

* For each required key in ``B``, the corresponding key is required
  in ``A``.  For each non-required key in ``B``, the corresponding key
  is not required in ``A``.

Discussion:

* Value types behave invariantly, since TypedDict objects are mutable.
  This is similar to mutable container types such as ``List`` and
  ``Dict``.  Example where this is relevant::

      class A(TypedDict):
          x: int | None

      class B(TypedDict):
          x: int

      def f(a: A) -> None:
          a['x'] = None

      b: B = {'x': 0}
      f(b)  # Type check error: 'B' not assignable to 'A'
      b['x'] + 1  # Runtime error: None + 1

* A TypedDict type with a required key is not :term:`assignable` to a TypedDict
  type where the same key is a non-required key, since the latter allows keys
  to be deleted.  Example where this is relevant::

      class A(TypedDict, total=False):
          x: int

      class B(TypedDict):
          x: int

      def f(a: A) -> None:
          del a['x']

      b: B = {'x': 0}
      f(b)  # Type check error: 'B' not assignable to 'A'
      b['x'] + 1  # Runtime KeyError: 'x'

* A TypedDict type ``A`` with no key ``'x'`` is not :term:`assignable` to a
  TypedDict type with a non-required key ``'x'``, since at runtime the key
  ``'x'`` could be present and have an :term:`inconsistent <consistent>` type
  (which may not be visible through ``A`` due to :term:`structural`
  assignability). Example::

      class A(TypedDict, total=False):
          x: int
          y: int

      class B(TypedDict, total=False):
          x: int

      class C(TypedDict, total=False):
          x: int
          y: str

       def f(a: A) -> None:
           a['y'] = 1

       def g(b: B) -> None:
           f(b)  # Type check error: 'B' not assignable to 'A'

       c: C = {'x': 0, 'y': 'foo'}
       g(c)
       c['y'] + 'bar'  # Runtime error: int + str

* A TypedDict isn't :term:`assignable` to any ``Dict[...]`` type, since
  dictionary types allow destructive operations, including ``clear()``.  They
  also allow arbitrary keys to be set, which would compromise type safety.
  Example::

      class A(TypedDict):
          x: int

      class B(A):
          y: str

      def f(d: Dict[str, int]) -> None:
          d['y'] = 0

      def g(a: A) -> None:
          f(a)  # Type check error: 'A' not assignable to Dict[str, int]

      b: B = {'x': 0, 'y': 'foo'}
      g(b)
      b['y'] + 'bar'  # Runtime error: int + str

* A TypedDict with all ``int`` values is not :term:`assignable` to
  ``Mapping[str, int]``, since there may be additional non-``int`` values not
  visible through the type, due to :term:`structural` assignability. These can
  be accessed using the ``values()`` and ``items()`` methods in ``Mapping``,
  for example.  Example::

      class A(TypedDict):
          x: int

      class B(TypedDict):
          x: int
          y: str

      def sum_values(m: Mapping[str, int]) -> int:
          n = 0
          for v in m.values():
              n += v  # Runtime error
          return n

      def f(a: A) -> None:
          sum_values(a)  # Error: 'A' not assignable to Mapping[str, int]

      b: B = {'x': 0, 'y': 'foo'}
      f(b)


Supported and Unsupported Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type checkers should support restricted forms of most ``dict``
operations on TypedDict objects.  The guiding principle is that
operations not involving ``Any`` types should be rejected by type
checkers if they may violate runtime type safety.  Here are some of
the most important type safety violations to prevent:

1. A required key is missing.

2. A value has an invalid type.

3. A key that is not defined in the TypedDict type is added.

A key that is not a literal should generally be rejected, since its
value is unknown during type checking, and thus can cause some of the
above violations.  (`Use of Final Values and Literal Types`_
generalizes this to cover final names and literal types.)

The use of a key that is not known to exist should be reported as an error,
even if this wouldn't necessarily generate a runtime type error.  These are
often mistakes, and these may insert values with an invalid type if
:term:`structural` :term:`assignability <assignable>` hides the types of
certain items. For example, ``d['x'] = 1`` should generate a type check error
if ``'x'`` is not a valid key for ``d`` (which is assumed to be a TypedDict
type).

Extra keys included in TypedDict object construction should also be
caught.  In this example, the ``director`` key is not defined in
``Movie`` and is expected to generate an error from a type checker::

    m: Movie = dict(
        name='Alien',
        year=1979,
        director='Ridley Scott')  # error: Unexpected key 'director'

Type checkers should reject the following operations on TypedDict
objects as unsafe, even though they are valid for normal dictionaries:

* Operations with arbitrary ``str`` keys (instead of string literals
  or other expressions with known string values) should generally be
  rejected.  This involves both destructive operations such as setting
  an item and read-only operations such as subscription expressions.
  As an exception to the above rule, ``d.get(e)`` and ``e in d``
  should be allowed for TypedDict objects, for an arbitrary expression
  ``e`` with type ``str``.  The motivation is that these are safe and
  can be useful for introspecting TypedDict objects.  The static type
  of ``d.get(e)`` should be ``object`` if the string value of ``e``
  cannot be determined statically.

* ``clear()`` is not safe since it could remove required keys, some of which
  may not be directly visible because of :term:`structural`
  :term:`assignability <assignable>`.  ``popitem()`` is similarly unsafe, even
  if all known keys are not required (``total=False``).

* ``del obj['key']`` should be rejected unless ``'key'`` is a
  non-required key.

Type checkers may allow reading an item using ``d['x']`` even if
the key ``'x'`` is not required, instead of requiring the use of
``d.get('x')`` or an explicit ``'x' in d`` check.  The rationale is
that tracking the existence of keys is difficult to implement in full
generality, and that disallowing this could require many changes to
existing code.

The exact type checking rules are up to each type checker to decide.
In some cases potentially unsafe operations may be accepted if the
alternative is to generate false positive errors for idiomatic code.


Use of Final Values and Literal Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Type checkers are only expected to support actual string literals, not
final names or literal types, for specifying keys in a TypedDict type
definition.  Also, only a boolean literal can be used to specify
totality in a TypedDict definition.  The motivation for this is to
make type declarations self-contained, and to simplify the
implementation of type checkers.


ClassVar and Final items
^^^^^^^^^^^^^^^^^^^^^^^^

``ClassVar`` and ``Final`` are not allowed as qualifiers for an item
of a ``TypedDict``. Such an item also causes a hard error at runtime.


Backwards Compatibility
^^^^^^^^^^^^^^^^^^^^^^^

To retain backwards compatibility, type checkers should not infer a
TypedDict type unless it is sufficiently clear that this is desired by
the programmer.  When unsure, an ordinary dictionary type should be
inferred.  Otherwise existing code that type checks without errors may
start generating errors once TypedDict support is added to the type
checker, since TypedDict types are more restrictive than dictionary
types.  In particular, they aren't subtypes of dictionary types.

.. _`required-notrequired`:

``Required`` and ``NotRequired``
--------------------------------

(Originally specified in :pep:`655`.)

.. _`required`:

The ``typing.Required`` :term:`type qualifier` is used to indicate that a
variable declared in a TypedDict definition is a required key:

::

   class Movie(TypedDict, total=False):
       title: Required[str]
       year: int

.. _`notrequired`:

Additionally the ``typing.NotRequired`` :term:`type qualifier` is used to
indicate that a variable declared in a TypedDict definition is a
potentially-missing key:

::

   class Movie(TypedDict):  # implicitly total=True
       title: str
       year: NotRequired[int]

It is an error to use ``Required[]`` or ``NotRequired[]`` in any
location that is not an item of a TypedDict.
Type checkers must enforce this restriction.

It is valid to use ``Required[]`` and ``NotRequired[]`` even for
items where it is redundant, to enable additional explicitness if desired:

::

   class Movie(TypedDict):
       title: Required[str]  # redundant
       year: NotRequired[int]

It is an error to use both ``Required[]`` and ``NotRequired[]`` at the
same time:

::

   class Movie(TypedDict):
       title: str
       year: NotRequired[Required[int]]  # ERROR

Type checkers must enforce this restriction.
The runtime implementations of ``Required[]`` and ``NotRequired[]``
may also enforce this restriction.

The :ref:`alternative functional syntax <typeddict-functional-syntax>`
for TypedDict also supports
``Required[]``, ``NotRequired[]``, and ``ReadOnly[]``:

::

   Movie = TypedDict('Movie', {'name': str, 'year': NotRequired[int]})


Interaction with ``total=False``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any TypedDict declared with ``total=False`` is equivalent
to a TypedDict with an implicit ``total=True`` definition with all of its
keys marked as ``NotRequired[]``.

Therefore:

::

   class _MovieBase(TypedDict):  # implicitly total=True
       title: str

   class Movie(_MovieBase, total=False):
       year: int


is equivalent to:

::

   class _MovieBase(TypedDict):
       title: str

   class Movie(_MovieBase):
       year: NotRequired[int]


Interaction with ``Annotated[]``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``Required[]`` and ``NotRequired[]`` can be used with ``Annotated[]``,
in any nesting order:

::

   class Movie(TypedDict):
       title: str
       year: NotRequired[Annotated[int, ValueRange(-9999, 9999)]]  # ok

::

   class Movie(TypedDict):
       title: str
       year: Annotated[NotRequired[int], ValueRange(-9999, 9999)]  # ok

In particular allowing ``Annotated[]`` to be the outermost annotation
for an item allows better interoperability with non-typing uses of
annotations, which may always want ``Annotated[]`` as the outermost annotation
(`discussion <https://bugs.python.org/issue46491>`__).


Read-only Items
---------------

(Originally specified in :pep:`705`.)

.. _`readonly`:

``typing.ReadOnly`` type qualifier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``typing.ReadOnly`` :term:`type qualifier` is used to indicate that an item declared in a ``TypedDict`` definition may not be mutated (added, modified, or removed)::

    from typing import ReadOnly

    class Band(TypedDict):
        name: str
        members: ReadOnly[list[str]]

    blur: Band = {"name": "blur", "members": []}
    blur["name"] = "Blur"  # OK: "name" is not read-only
    blur["members"] = ["Damon Albarn"]  # Type check error: "members" is read-only
    blur["members"].append("Damon Albarn")  # OK: list is mutable


Interaction with other special types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``ReadOnly[]`` can be used with ``Required[]``, ``NotRequired[]`` and ``Annotated[]``, in any nesting order:

::

    class Movie(TypedDict):
        title: ReadOnly[Required[str]]  # OK
        year: ReadOnly[NotRequired[Annotated[int, ValueRange(-9999, 9999)]]]  # OK

::

    class Movie(TypedDict):
        title: Required[ReadOnly[str]]  # OK
        year: Annotated[NotRequired[ReadOnly[int]], ValueRange(-9999, 9999)]  # OK


Inheritance
^^^^^^^^^^^

Subclasses can redeclare read-only items as non-read-only, allowing them to be mutated::

    class NamedDict(TypedDict):
        name: ReadOnly[str]

    class Album(NamedDict):
        name: str
        year: int

    album: Album = { "name": "Flood", "year": 1990 }
    album["year"] = 1973
    album["name"] = "Dark Side Of The Moon"  # OK: "name" is not read-only in Album

If a read-only item is not redeclared, it remains read-only::

    class Album(NamedDict):
        year: int

    album: Album = { "name": "Flood", "year": 1990 }
    album["name"] = "Dark Side Of The Moon"  # Type check error: "name" is read-only in Album

Subclasses can narrow value types of read-only items::

    class AlbumCollection(TypedDict):
        albums: ReadOnly[Collection[Album]]

    class RecordShop(AlbumCollection):
        name: str
        albums: ReadOnly[list[Album]]  # OK: "albums" is read-only in AlbumCollection

Subclasses can require items that are read-only but not required in the superclass::

    class OptionalName(TypedDict):
        name: ReadOnly[NotRequired[str]]

    class RequiredName(OptionalName):
        name: ReadOnly[Required[str]]

    d: RequiredName = {}  # Type check error: "name" required

Subclasses can combine these rules::

    class OptionalIdent(TypedDict):
        ident: ReadOnly[NotRequired[str | int]]

    class User(OptionalIdent):
        ident: str  # Required, mutable, and not an int

Note that these are just consequences of :term:`structural` typing, but they
are highlighted here as the behavior now differs from the rules specified in
:pep:`589`.

Assignability
^^^^^^^^^^^^^

*This section updates the assignability rules described above that were created
prior to the introduction of ReadOnly*

A TypedDict type ``B`` is :term:`assignable` to a TypedDict type ``A`` if ``B``
is :term:`structurally <structural>` assignable to ``A``. This is true if and
only if all of the following are satisfied:

* For each item in ``A``, ``B`` has the corresponding key, unless the item in
  ``A`` is read-only, not required, and of top value type
  (``ReadOnly[NotRequired[object]]``).
* For each item in ``A``, if ``B`` has the corresponding key, the corresponding
  value type in ``B`` is assignable to the value type in ``A``.
* For each non-read-only item in ``A``, its value type is assignable to the
  corresponding value type in ``B``, and the corresponding key is not read-only
  in ``B``.
* For each required key in ``A``, the corresponding key is required in ``B``.
* For each non-required key in ``A``, if the item is not read-only in ``A``,
  the corresponding key is not required in ``B``.

Discussion:

* All non-specified items in a TypedDict implicitly have value type
  ``ReadOnly[NotRequired[object]]``.

* Read-only items behave covariantly, as they cannot be mutated. This is
  similar to container types such as ``Sequence``, and different from
  non-read-only items, which behave invariantly. Example::

    class A(TypedDict):
        x: ReadOnly[int | None]

    class B(TypedDict):
        x: int

    def f(a: A) -> None:
        print(a["x"] or 0)

    b: B = {"x": 1}
    f(b)  # Accepted by type checker

* A TypedDict type ``A`` with no explicit key ``'x'`` is not :term:`assignable`
  to a TypedDict type ``B`` with a non-required key ``'x'``, since at runtime
  the key ``'x'`` could be present and have an :term:`inconsistent
  <consistent>` type (which may not be visible through ``A`` due to
  :term:`structural` typing). The only exception to this rule is if the item in
  ``B`` is read-only, and the value type is of top type (``object``). For
  example::

    class A(TypedDict):
        x: int

    class B(TypedDict):
        x: int
        y: ReadOnly[NotRequired[object]]

    a: A = { "x": 1 }
    b: B = a  # Accepted by type checker

Update method
^^^^^^^^^^^^^

In addition to existing type checking rules, type checkers should error if a
TypedDict with a read-only item is updated with another TypedDict that declares
that key::

    class A(TypedDict):
        x: ReadOnly[int]
        y: int

    a1: A = { "x": 1, "y": 2 }
    a2: A = { "x": 3, "y": 4 }
    a1.update(a2)  # Type check error: "x" is read-only in A

Unless the declared value is of bottom type (:data:`~typing.Never`)::

    class B(TypedDict):
        x: NotRequired[typing.Never]
        y: ReadOnly[int]

    def update_a(a: A, b: B) -> None:
        a.update(b)  # Accepted by type checker: "x" cannot be set on b

Note: Nothing will ever match the ``Never`` type, so an item annotated with it must be absent.

Keyword argument typing
^^^^^^^^^^^^^^^^^^^^^^^

As discussed in the section :ref:`unpack-kwargs`, an unpacked ``TypedDict`` can be used to annotate ``**kwargs``. Marking one or more of the items of a ``TypedDict`` used in this way as read-only will have no effect on the type signature of the method. However, it *will* prevent the item from being modified in the body of the function::

    class Args(TypedDict):
        key1: int
        key2: str

    class ReadOnlyArgs(TypedDict):
        key1: ReadOnly[int]
        key2: ReadOnly[str]

    class Function(Protocol):
        def __call__(self, **kwargs: Unpack[Args]) -> None: ...

    def impl(**kwargs: Unpack[ReadOnlyArgs]) -> None:
        kwargs["key1"] = 3  # Type check error: key1 is readonly

    fn: Function = impl  # Accepted by type checker: function signatures are identical
