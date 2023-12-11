Literals
========

``Literal``
-----------

(Originally specified in :pep:`586`.)


Core Semantics
^^^^^^^^^^^^^^

This section outlines the baseline behavior of literal types.

Core behavior
"""""""""""""

Literal types indicate that a variable has a specific and
concrete value. For example, if we define some variable ``foo`` to have
type ``Literal[3]``, we are declaring that ``foo`` must be exactly equal
to ``3`` and no other value.

Given some value ``v`` that is a member of type ``T``, the type
``Literal[v]`` shall be treated as a subtype of ``T``. For example,
``Literal[3]`` is a subtype of ``int``.

All methods from the parent type will be directly inherited by the
literal type. So, if we have some variable ``foo`` of type ``Literal[3]``
it’s safe to do things like ``foo + 5`` since ``foo`` inherits ``int``’s
``__add__`` method. The resulting type of ``foo + 5`` is ``int``.

This "inheriting" behavior is identical to how we
:pep:`handle NewTypes <484#newtype-helper-function>`.

Equivalence of two Literals
"""""""""""""""""""""""""""

Two types ``Literal[v1]`` and ``Literal[v2]`` are equivalent when
both of the following conditions are true:

1. ``type(v1) == type(v2)``
2. ``v1 == v2``

For example, ``Literal[20]`` and ``Literal[0x14]`` are equivalent.
However, ``Literal[0]`` and ``Literal[False]`` are *not* equivalent
despite that ``0 == False`` evaluates to 'true' at runtime: ``0``
has type ``int`` and ``False`` has type ``bool``.

Shortening unions of literals
"""""""""""""""""""""""""""""

Literals are parameterized with one or more values. When a Literal is
parameterized with more than one value, it's treated as exactly equivalent
to the union of those types. That is, ``Literal[v1, v2, v3]`` is equivalent
to ``Literal[v1] | Literal[v2] | Literal[v3]``.

This shortcut helps make writing signatures for functions that accept
many different literals more ergonomic — for example, functions like
``open(...)``::

   # Note: this is a simplification of the true type signature.
   _PathType = str | bytes | int

   @overload
   def open(path: _PathType,
            mode: Literal["r", "w", "a", "x", "r+", "w+", "a+", "x+"],
            ) -> IO[str]: ...
   @overload
   def open(path: _PathType,
            mode: Literal["rb", "wb", "ab", "xb", "r+b", "w+b", "a+b", "x+b"],
            ) -> IO[bytes]: ...

   # Fallback overload for when the user isn't using literal types
   @overload
   def open(path: _PathType, mode: str) -> IO[Any]: ...

The provided values do not all have to be members of the same type.
For example, ``Literal[42, "foo", True]`` is a legal type.

However, Literal **must** be parameterized with at least one type.
Types like ``Literal[]`` or ``Literal`` are illegal.


Legal and illegal parameterizations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This section describes what exactly constitutes a legal ``Literal[...]`` type:
what values may and may not be used as parameters.

In short, a ``Literal[...]`` type may be parameterized by one or more literal
expressions, and nothing else.


Legal parameters for ``Literal`` at type check time
"""""""""""""""""""""""""""""""""""""""""""""""""""

``Literal`` may be parameterized with literal ints, byte and unicode strings,
bools, Enum values and ``None``. So for example, all of
the following would be legal::

   Literal[26]
   Literal[0x1A]  # Exactly equivalent to Literal[26]
   Literal[-4]
   Literal["hello world"]
   Literal[b"hello world"]
   Literal[u"hello world"]
   Literal[True]
   Literal[Color.RED]  # Assuming Color is some enum
   Literal[None]

**Note:** Since the type ``None`` is inhabited by just a single
value, the types ``None`` and ``Literal[None]`` are exactly equivalent.
Type checkers may simplify ``Literal[None]`` into just ``None``.

``Literal`` may also be parameterized by other literal types, or type aliases
to other literal types. For example, the following is legal::

    ReadOnlyMode         = Literal["r", "r+"]
    WriteAndTruncateMode = Literal["w", "w+", "wt", "w+t"]
    WriteNoTruncateMode  = Literal["r+", "r+t"]
    AppendMode           = Literal["a", "a+", "at", "a+t"]

    AllModes = Literal[ReadOnlyMode, WriteAndTruncateMode,
                       WriteNoTruncateMode, AppendMode]

This feature is again intended to help make using and reusing literal types
more ergonomic.

**Note:** As a consequence of the above rules, type checkers are also expected
to support types that look like the following::

    Literal[Literal[Literal[1, 2, 3], "foo"], 5, None]

This should be exactly equivalent to the following type::

    Literal[1, 2, 3, "foo", 5, None]

...and also to the following type::

    Literal[1, 2, 3, "foo", 5] | None

**Note:** String literal types like ``Literal["foo"]`` should subtype either
bytes or unicode in the same way regular string literals do at runtime.

For example, in Python 3, the type ``Literal["foo"]`` is equivalent to
``Literal[u"foo"]``, since ``"foo"`` is equivalent to ``u"foo"`` in Python 3.

Similarly, in Python 2, the type ``Literal["foo"]`` is equivalent to
``Literal[b"foo"]`` -- unless the file includes a
``from __future__ import unicode_literals`` import, in which case it would be
equivalent to ``Literal[u"foo"]``.

Illegal parameters for ``Literal`` at type check time
"""""""""""""""""""""""""""""""""""""""""""""""""""""

The following parameters are intentionally disallowed by design:

- Arbitrary expressions like ``Literal[3 + 4]`` or
  ``Literal["foo".replace("o", "b")]``.

  - Rationale: Literal types are meant to be a
    minimal extension to the :pep:`484` typing ecosystem and requiring type
    checkers to interpret potentially expressions inside types adds too
    much complexity.

  - As a consequence, complex numbers like ``Literal[4 + 3j]`` and
    ``Literal[-4 + 2j]`` are also prohibited. For consistency, literals like
    ``Literal[4j]`` that contain just a single complex number are also
    prohibited.

  - The only exception to this rule is the unary ``-`` (minus) for ints: types
    like ``Literal[-5]`` are *accepted*.

-  Tuples containing valid literal types like ``Literal[(1, "foo", "bar")]``.
   The user could always express this type as
   ``tuple[Literal[1], Literal["foo"], Literal["bar"]]`` instead. Also,
   tuples are likely to be confused with the ``Literal[1, 2, 3]``
   shortcut.

-  Mutable literal data structures like dict literals, list literals, or
   set literals: literals are always implicitly final and immutable. So,
   ``Literal[{"a": "b", "c": "d"}]`` is illegal.

-  Any other types: for example, ``Literal[Path]``, or
   ``Literal[some_object_instance]`` are illegal. This includes typevars: if
   ``T`` is a typevar,  ``Literal[T]`` is not allowed. Typevars can vary over
   only types, never over values.

The following are provisionally disallowed for simplicity. We can consider
allowing them in the future.

-  Floats: e.g. ``Literal[3.14]``. Representing Literals of infinity or NaN
   in a clean way is tricky; real-world APIs are unlikely to vary their
   behavior based on a float parameter.

-  Any: e.g. ``Literal[Any]``. ``Any`` is a type, and ``Literal[...]`` is
   meant to contain values only. It is also unclear what ``Literal[Any]``
   would actually semantically mean.

Parameters at runtime
"""""""""""""""""""""

Although the set of parameters ``Literal[...]`` may contain at type check time
is very small, the actual implementation of ``typing.Literal`` will not perform
any checks at runtime. For example::

   def my_function(x: Literal[1 + 2]) -> int:
       return x * 3

   x: Literal = 3
   y: Literal[my_function] = my_function

The type checker should reject this program: all three uses of
``Literal`` are *invalid* according to this spec. However, Python itself
should execute this program with no errors.

This is partly to help us preserve flexibility in case we want to expand the
scope of what ``Literal`` can be used for in the future, and partly because
it is not possible to detect all illegal parameters at runtime to begin with.
For example, it is impossible to distinguish between ``Literal[1 + 2]`` and
``Literal[3]`` at runtime.

Literals, enums, and forward references
"""""""""""""""""""""""""""""""""""""""

One potential ambiguity is between literal strings and forward
references to literal enum members. For example, suppose we have the
type ``Literal["Color.RED"]``. Does this literal type
contain a string literal or a forward reference to some ``Color.RED``
enum member?

In cases like these, we always assume the user meant to construct a
literal string. If the user wants a forward reference, they must wrap
the entire literal type in a string -- e.g. ``"Literal[Color.RED]"``.

Type inference
^^^^^^^^^^^^^^

This section describes a few rules regarding type inference and
literals, along with some examples.

Backwards compatibility
"""""""""""""""""""""""

When type checkers add support for Literal, it's important they do so
in a way that maximizes backwards-compatibility. Type checkers should
ensure that code that used to type check continues to do so after support
for Literal is added on a best-effort basis.

This is particularly important when performing type inference. For
example, given the statement ``x = "blue"``, should the inferred
type of ``x`` be ``str`` or ``Literal["blue"]``?

One naive strategy would be to always assume expressions are intended
to be Literal types. So, ``x`` would always have an inferred type of
``Literal["blue"]`` in the example above. This naive strategy is almost
certainly too disruptive -- it would cause programs like the following
to start failing when they previously did not::

    # If a type checker infers 'var' has type Literal[3]
    # and my_list has type List[Literal[3]]...
    var = 3
    my_list = [var]

    # ...this call would be a type-error.
    my_list.append(4)

Another example of when this strategy would fail is when setting fields
in objects::

    class MyObject:
        def __init__(self) -> None:
            # If a type checker infers MyObject.field has type Literal[3]...
            self.field = 3

    m = MyObject()

    # ...this assignment would no longer type check
    m.field = 4

An alternative strategy that *does* maintain compatibility in every case would
be to always assume expressions are *not* Literal types unless they are
explicitly annotated otherwise. A type checker using this strategy would
always infer that ``x`` is of type ``str`` in the first example above.

This is not the only viable strategy: type checkers should feel free to experiment
with more sophisticated inference techniques. No particular strategy is
mandated, but type checkers should keep in mind the importance of backwards
compatibility.

Using non-Literals in Literal contexts
""""""""""""""""""""""""""""""""""""""

Literal types follow the existing rules regarding subtyping with no additional
special-casing. For example, programs like the following are type safe::

   def expects_str(x: str) -> None: ...
   var: Literal["foo"] = "foo"

   # Legal: Literal["foo"] is a subtype of str
   expects_str(var)

This also means non-Literal expressions in general should not automatically
be cast to Literal. For example::

   def expects_literal(x: Literal["foo"]) -> None: ...

   def runner(my_str: str) -> None:
       # ILLEGAL: str is not a subclass of Literal["foo"]
       expects_literal(my_str)

**Note:** If the user wants their API to support accepting both literals
*and* the original type -- perhaps for legacy purposes -- they should
implement a fallback overload. See :ref:`literalstring-overloads`.

Interactions with other types and features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This section discusses how Literal types interact with other existing types.

Intelligent indexing of structured data
"""""""""""""""""""""""""""""""""""""""

Literals can be used to "intelligently index" into structured types like
tuples, NamedTuple, and classes. (Note: this is not an exhaustive list).

For example, type checkers should infer the correct value type when
indexing into a tuple using an int key that corresponds a valid index::

   a: Literal[0] = 0
   b: Literal[5] = 5

   some_tuple: tuple[int, str, List[bool]] = (3, "abc", [True, False])
   reveal_type(some_tuple[a])   # Revealed type is 'int'
   some_tuple[b]                # Error: 5 is not a valid index into the tuple

We expect similar behavior when using functions like getattr::

   class Test:
       def __init__(self, param: int) -> None:
           self.myfield = param

       def mymethod(self, val: int) -> str: ...

   a: Literal["myfield"]  = "myfield"
   b: Literal["mymethod"] = "mymethod"
   c: Literal["blah"]     = "blah"

   t = Test()
   reveal_type(getattr(t, a))  # Revealed type is 'int'
   reveal_type(getattr(t, b))  # Revealed type is 'Callable[[int], str]'
   getattr(t, c)               # Error: No attribute named 'blah' in Test

**Note:** See `Interactions with Final`_ for how we can
express the variable declarations above in a more compact manner.

Interactions with overloads
"""""""""""""""""""""""""""

Literal types and overloads do not need to interact in  a special
way: the existing rules work fine.

However, one important use case type checkers must take care to
support is the ability to use a *fallback* when the user is not using literal
types. For example, consider ``open``::

   _PathType = str | bytes | int

   @overload
   def open(path: _PathType,
            mode: Literal["r", "w", "a", "x", "r+", "w+", "a+", "x+"],
            ) -> IO[str]: ...
   @overload
   def open(path: _PathType,
            mode: Literal["rb", "wb", "ab", "xb", "r+b", "w+b", "a+b", "x+b"],
            ) -> IO[bytes]: ...

   # Fallback overload for when the user isn't using literal types
   @overload
   def open(path: _PathType, mode: str) -> IO[Any]: ...

If we were to change the signature of ``open`` to use just the first two overloads,
we would break any code that does not pass in a literal string expression.
For example, code like this would be broken::

   mode: str = pick_file_mode(...)
   with open(path, mode) as f:
       # f should continue to be of type IO[Any] here

A little more broadly: we mandate that whenever we add literal types to
some existing API in typeshed, we also always include a fallback overload to
maintain backwards-compatibility.

Interactions with generics
""""""""""""""""""""""""""

Types like ``Literal[3]`` are meant to be just plain old subclasses of
``int``. This means you can use types like ``Literal[3]`` anywhere
you could use normal types, such as with generics.

This means that it is legal to parameterize generic functions or
classes using Literal types::

   A = TypeVar('A', bound=int)
   B = TypeVar('B', bound=int)
   C = TypeVar('C', bound=int)

   # A simplified definition for Matrix[row, column]
   class Matrix(Generic[A, B]):
       def __add__(self, other: Matrix[A, B]) -> Matrix[A, B]: ...
       def __matmul__(self, other: Matrix[B, C]) -> Matrix[A, C]: ...
       def transpose(self) -> Matrix[B, A]: ...

   foo: Matrix[Literal[2], Literal[3]] = Matrix(...)
   bar: Matrix[Literal[3], Literal[7]] = Matrix(...)

   baz = foo @ bar
   reveal_type(baz)  # Revealed type is 'Matrix[Literal[2], Literal[7]]'

Similarly, it is legal to construct TypeVars with value restrictions
or bounds involving Literal types::

   T = TypeVar('T', Literal["a"], Literal["b"], Literal["c"])
   S = TypeVar('S', bound=Literal["foo"])

...although it is unclear when it would ever be useful to construct a
TypeVar with a Literal upper bound. For example, the ``S`` TypeVar in
the above example is essentially pointless: we can get equivalent behavior
by using ``S = Literal["foo"]`` instead.

**Note:** Literal types and generics deliberately interact in only very
basic and limited ways. In particular, libraries that want to type check
code containing a heavy amount of numeric or numpy-style manipulation will
almost certainly likely find Literal types as described here to be
insufficient for their needs.

Interactions with enums and exhaustiveness checks
"""""""""""""""""""""""""""""""""""""""""""""""""

Type checkers should be capable of performing exhaustiveness checks when
working Literal types that have a closed number of variants, such as
enums. For example, the type checker should be capable of inferring that
the final ``else`` statement must be of type ``str``, since all three
values of the ``Status`` enum have already been exhausted::

    class Status(Enum):
        SUCCESS = 0
        INVALID_DATA = 1
        FATAL_ERROR = 2

    def parse_status(s: str | Status) -> None:
        if s is Status.SUCCESS:
            print("Success!")
        elif s is Status.INVALID_DATA:
            print("The given data is invalid because...")
        elif s is Status.FATAL_ERROR:
            print("Unexpected fatal error...")
        else:
            # 's' must be of type 'str' since all other options are exhausted
            print("Got custom status: " + s)

The interaction described above is not new: it's already
:pep:`codified within PEP 484 <484#support-for-singleton-types-in-unions>`.
However, many type
checkers (such as mypy) do not yet implement this due to the expected
complexity of the implementation work.

Some of this complexity will be alleviated once Literal types are introduced:
rather than entirely special-casing enums, we can instead treat them as being
approximately equivalent to the union of their values and take advantage of any
existing logic regarding unions, exhaustibility, type narrowing, reachability,
and so forth the type checker might have already implemented.

So here, the ``Status`` enum could be treated as being approximately equivalent
to ``Literal[Status.SUCCESS, Status.INVALID_DATA, Status.FATAL_ERROR]``
and the type of ``s`` narrowed accordingly.

Interactions with narrowing
"""""""""""""""""""""""""""

Type checkers may optionally perform additional analysis for both enum and
non-enum Literal types beyond what is described in the section above.

For example, it may be useful to perform narrowing based on things like
containment or equality checks::

   def parse_status(status: str) -> None:
       if status in ("MALFORMED", "ABORTED"):
           # Type checker could narrow 'status' to type
           # Literal["MALFORMED", "ABORTED"] here.
           return expects_bad_status(status)

       # Similarly, type checker could narrow 'status' to Literal["PENDING"]
       if status == "PENDING":
           expects_pending_status(status)

It may also be useful to perform narrowing taking into account expressions
involving Literal bools. For example, we can combine ``Literal[True]``,
``Literal[False]``, and overloads to construct "custom type guards"::

   @overload
   def is_int_like(x: int | list[int]) -> Literal[True]: ...
   @overload
   def is_int_like(x: object) -> bool: ...
   def is_int_like(x): ...

   vector: list[int] = [1, 2, 3]
   if is_int_like(vector):
       vector.append(3)
   else:
       vector.append("bad")   # This branch is inferred to be unreachable

   scalar: int | str
   if is_int_like(scalar):
       scalar += 3      # Type checks: type of 'scalar' is narrowed to 'int'
   else:
       scalar += "foo"  # Type checks: type of 'scalar' is narrowed to 'str'

Interactions with Final
"""""""""""""""""""""""

The ``Final`` qualifier can be used to declare that some variable or
attribute cannot be reassigned::

    foo: Final = 3
    foo = 4           # Error: 'foo' is declared to be Final

Note that in the example above, we know that ``foo`` will always be equal to
exactly ``3``. A type checker can use this information to deduce that ``foo``
is valid to use in any context that expects a ``Literal[3]``::

    def expects_three(x: Literal[3]) -> None: ...

    expects_three(foo)  # Type checks, since 'foo' is Final and equal to 3

The ``Final`` qualifier serves as a shorthand for declaring that a variable
is *effectively Literal*.

Type checkers are expected to
support this shortcut. Specifically, given a variable or attribute assignment
of the form ``var: Final = value`` where ``value`` is a valid parameter for
``Literal[...]``, type checkers should understand that ``var`` may be used in
any context that expects a ``Literal[value]``.

Type checkers are not obligated to understand any other uses of Final. For
example, whether or not the following program type checks is left unspecified::

    # Note: The assignment does not exactly match the form 'var: Final = value'.
    bar1: Final[int] = 3
    expects_three(bar1)  # May or may not be accepted by type checkers

    # Note: "Literal[1 + 2]" is not a legal type.
    bar2: Final = 1 + 2
    expects_three(bar2)  # May or may not be accepted by type checkers

``LiteralString``
-----------------

(Originally specified in :pep:`675`.)

Valid locations for ``LiteralString``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``LiteralString`` can be used where any other type can be used:

::

    variable_annotation: LiteralString

    def my_function(literal_string: LiteralString) -> LiteralString: ...

    class Foo:
        my_attribute: LiteralString

    type_argument: List[LiteralString]

    T = TypeVar("T", bound=LiteralString)

It cannot be nested within unions of ``Literal`` types:

::

    bad_union: Literal["hello", LiteralString]  # Not OK
    bad_nesting: Literal[LiteralString]  # Not OK


Type inference
^^^^^^^^^^^^^^

Inferring ``LiteralString``
"""""""""""""""""""""""""""

Any literal string type is compatible with ``LiteralString``. For
example, ``x: LiteralString = "foo"`` is valid because ``"foo"`` is
inferred to be of type ``Literal["foo"]``.

We also infer ``LiteralString`` in the
following cases:

+ Addition: ``x + y`` is of type ``LiteralString`` if both ``x`` and
  ``y`` are compatible with ``LiteralString``.

+ Joining: ``sep.join(xs)`` is of type ``LiteralString`` if ``sep``'s
  type is compatible with ``LiteralString`` and ``xs``'s type is
  compatible with ``Iterable[LiteralString]``.

+ In-place addition: If ``s`` has type ``LiteralString`` and ``x`` has
  type compatible with ``LiteralString``, then ``s += x`` preserves
  ``s``'s type as ``LiteralString``.

+ String formatting: An f-string has type ``LiteralString`` if and only
  if its constituent expressions are literal strings. ``s.format(...)``
  has type ``LiteralString`` if and only if ``s`` and the arguments have
  types compatible with ``LiteralString``.

In all other cases, if one or more of the composed values has a
non-literal type ``str``, the composition of types will have type
``str``. For example, if ``s`` has type ``str``, then ``"hello" + s``
has type ``str``. This matches the pre-existing behavior of type
checkers.

``LiteralString`` is compatible with the type ``str``. It inherits all
methods from ``str``. So, if we have a variable ``s`` of type
``LiteralString``, it is safe to write ``s.startswith("hello")``.

Some type checkers refine the type of a string when doing an equality
check:

::

    def foo(s: str) -> None:
        if s == "bar":
            reveal_type(s)  # => Literal["bar"]

Such a refined type in the if-block is also compatible with
``LiteralString`` because its type is ``Literal["bar"]``.


Examples
""""""""

See the examples below to help clarify the above rules:

::


    literal_string: LiteralString
    s: str = literal_string  # OK

    literal_string: LiteralString = s  # Error: Expected LiteralString, got str.
    literal_string: LiteralString = "hello"  # OK

Addition of literal strings:

::

    def expect_literal_string(s: LiteralString) -> None: ...

    expect_literal_string("foo" + "bar")  # OK
    expect_literal_string(literal_string + "bar")  # OK

    literal_string2: LiteralString
    expect_literal_string(literal_string + literal_string2)  # OK

    plain_string: str
    expect_literal_string(literal_string + plain_string)  # Not OK.

Join using literal strings:

::

    expect_literal_string(",".join(["foo", "bar"]))  # OK
    expect_literal_string(literal_string.join(["foo", "bar"]))  # OK
    expect_literal_string(literal_string.join([literal_string, literal_string2]))  # OK

    xs: List[LiteralString]
    expect_literal_string(literal_string.join(xs)) # OK
    expect_literal_string(plain_string.join([literal_string, literal_string2]))
    # Not OK because the separator has type 'str'.

In-place addition using literal strings:

::

    literal_string += "foo"  # OK
    literal_string += literal_string2  # OK
    literal_string += plain_string # Not OK

Format strings using literal strings:

::

    literal_name: LiteralString
    expect_literal_string(f"hello {literal_name}")
    # OK because it is composed from literal strings.

    expect_literal_string("hello {}".format(literal_name))  # OK

    expect_literal_string(f"hello")  # OK

    username: str
    expect_literal_string(f"hello {username}")
    # NOT OK. The format-string is constructed from 'username',
    # which has type 'str'.

    expect_literal_string("hello {}".format(username))  # Not OK

Other literal types, such as literal integers, are not compatible with ``LiteralString``:

::

    some_int: int
    expect_literal_string(some_int)  # Error: Expected LiteralString, got int.

    literal_one: Literal[1] = 1
    expect_literal_string(literal_one)  # Error: Expected LiteralString, got Literal[1].


We can call functions on literal strings:

::

    def add_limit(query: LiteralString) -> LiteralString:
        return query + " LIMIT = 1"

    def my_query(query: LiteralString, user_id: str) -> None:
        sql_connection().execute(add_limit(query), (user_id,))  # OK

Conditional statements and expressions work as expected:

::

    def return_literal_string() -> LiteralString:
        return "foo" if condition1() else "bar"  # OK

    def return_literal_str2(literal_string: LiteralString) -> LiteralString:
        return "foo" if condition1() else literal_string  # OK

    def return_literal_str3() -> LiteralString:
        if condition1():
            result: Literal["foo"] = "foo"
        else:
            result: LiteralString = "bar"

        return result  # OK


Interaction with TypeVars and Generics
""""""""""""""""""""""""""""""""""""""

TypeVars can be bound to ``LiteralString``:

::

    from typing import Literal, LiteralString, TypeVar

    TLiteral = TypeVar("TLiteral", bound=LiteralString)

    def literal_identity(s: TLiteral) -> TLiteral:
        return s

    hello: Literal["hello"] = "hello"
    y = literal_identity(hello)
    reveal_type(y)  # => Literal["hello"]

    s: LiteralString
    y2 = literal_identity(s)
    reveal_type(y2)  # => LiteralString

    s_error: str
    literal_identity(s_error)
    # Error: Expected TLiteral (bound to LiteralString), got str.


``LiteralString`` can be used as a type argument for generic classes:

::

    class Container(Generic[T]):
        def __init__(self, value: T) -> None:
            self.value = value

    literal_string: LiteralString = "hello"
    x: Container[LiteralString] = Container(literal_string)  # OK

    s: str
    x_error: Container[LiteralString] = Container(s)  # Not OK

Standard containers like ``List`` work as expected:

::

    xs: List[LiteralString] = ["foo", "bar", "baz"]


.. _literalstring-overloads:

Interactions with Overloads
"""""""""""""""""""""""""""

Literal strings and overloads do not need to interact in a special
way: the existing rules work fine. ``LiteralString`` can be used as a
fallback overload where a specific ``Literal["foo"]`` type does not
match:

::

    @overload
    def foo(x: Literal["foo"]) -> int: ...
    @overload
    def foo(x: LiteralString) -> bool: ...
    @overload
    def foo(x: str) -> str: ...

    x1: int = foo("foo")  # First overload.
    x2: bool = foo("bar")  # Second overload.
    s: str
    x3: str = foo(s)  # Third overload.
