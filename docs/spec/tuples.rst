.. _`tuples`:

Tuples
======

The ``tuple`` class has some special behaviors and properties that make it
different from other classes from a typing perspective. The most obvious
difference is that ``tuple`` is variadic -- it supports an arbitrary number
of type arguments. At runtime, the sequence of objects contained within the
tuple is fixed at the time of construction. Elements cannot be added, removed,
reordered, or replaced after construction. These properties affect subtyping
rules and other behaviors as described below.


Tuple Type Form
---------------

The type of a tuple can be expressed by listing the element types. For
example, ``tuple[int, int, str]`` is a tuple containing an ``int``, another
``int``, and a ``str``.

The empty tuple can be annotated as ``tuple[()]``.

Arbitrary-length homogeneous tuples can be expressed using one type and an
ellipsis, for example ``tuple[int, ...]``. This type is equivalent to a union
of tuples containing zero or more ``int`` elements (``tuple[()] |
tuple[int] | tuple[int, int] | tuple[int, int, int] | ...``).
Arbitrary-length homogeneous tuples are sometimes referred to as "unbounded
tuples". Both of these terms appear within the typing spec, and they refer to
the same concept.

The type ``tuple[Any, ...]`` is special in that it is bidirectionally
compatible with any tuple of any length. This is useful for gradual typing.
The type ``tuple`` (with no type arguments provided) is equivalent to
``tuple[Any, ...]``.

Arbitrary-length tuples have exactly two type arguments -- the type and
an ellipsis. Any other tuple form that uses an ellipsis is invalid::

    t1: tuple[int, ...]  # OK
    t2: tuple[int, int, ...]  # Invalid
    t3: tuple[...]  # Invalid
    t4: tuple[..., int]  # Invalid
    t5: tuple[int, ..., int]  # Invalid
    t6: tuple[*tuple[str], ...]  # Invalid
    t7: tuple[*tuple[str, ...], ...]  # Invalid


Unpacked Tuple Form
-------------------

An unpacked form of ``tuple`` (using an unpack operator ``*``) can be used
within a tuple type argument list. For example, ``tuple[int, *tuple[str]]``
is equivalent to ``tuple[int, str]``. Unpacking an unbounded tuple preserves
the unbounded tuple as it is. That is, ``*tuple[int, ...]`` remains
``*tuple[int, ...]``; there's no simpler form. This enables us to specify
types such as ``tuple[int, *tuple[str, ...], str]`` -- a tuple type where the
first element is guaranteed to be of type ``int``, the last element is
guaranteed to be of type ``str``, and the elements in the middle are zero or
more elements of type ``str``. The type ``tuple[*tuple[int, ...]]`` is
equivalent to ``tuple[int, ...]``.

If an unpacked ``*tuple[Any, ...]`` is embedded within another tuple, that
portion of the tuple is bidirectionally type compatible with any tuple of
any length.

Only one unbounded tuple can be used within another tuple::

    t1: tuple[*tuple[str], *tuple[str]]  # OK
    t2: tuple[*tuple[str, *tuple[str, ...]]]  # OK
    t3: tuple[*tuple[str, ...], *tuple[int, ...]]  # Type error
    t4: tuple[*tuple[str, *tuple[str, ...]], *tuple[int, ...]]  # Type error

An unpacked TypeVarTuple counts as an unbounded tuple in the context of this rule::

    def func[*Ts](t: tuple[*Ts]):
        t5: tuple[*tuple[str], *Ts]  # OK
        t6: tuple[*tuple[str, ...], *Ts]  # Type error

The ``*`` syntax requires Python 3.11 or newer. For older versions of Python,
the ``typing.Unpack`` :term:`special form` can be used:
``tuple[int, Unpack[tuple[str, ...]], int]``.

Unpacked tuples can also be used for ``*args`` parameters in a function
signature: ``def f(*args: *tuple[int, str]): ...``. Unpacked tuples
can also be used for specializing generic classes or type variables that are
parameterized using a ``TypeVarTuple``. For more details, see
:ref:`args_as_typevartuple`.


Type Compatibility Rules
------------------------

Because tuple contents are immutable, the element types of a tuple are covariant.
For example, ``tuple[int, int]`` is a subtype of ``tuple[float, complex]``.

As discussed above, a homogeneous tuple of arbitrary length is equivalent
to a union of tuples of different lengths. That means ``tuple[()]``,
``tuple[int]`` and ``tuple[int, *tuple[int, ...]]`` are all subtypes of
``tuple[int, ...]``. The converse is not true; ``tuple[int, ...]`` is not a
subtype of ``tuple[int]``.

The type ``tuple[Any, ...]`` is bidirectionally compatible with any tuple::

    def func(t1: tuple[int], t2: tuple[int, ...], t3: tuple[Any, ...]):
        v1: tuple[int, ...] = t1  # OK
        v2: tuple[Any, ...] = t1  # OK

        v3: tuple[int] = t2  # Type error
        v4: tuple[Any, ...] = t2  # OK

        v5: tuple[float, float] = t3  # OK
        v6: tuple[int, *tuple[str, ...]] = t3  # OK


The length of a tuple at runtime is immutable, so it is safe for type checkers
to use length checks to narrow the type of a tuple::

    def func(val: tuple[int] | tuple[str, str] | tuple[int, *tuple[str, ...], int]):
        if len(val) == 1:
            # Type can be narrowed to tuple[int].
            reveal_type(val)  # tuple[int]

        if len(val) == 2:
            # Type can be narrowed to tuple[str, str] | tuple[int, int].
            reveal_type(val)  # tuple[str, str] | tuple[int, int]

        if len(val) == 3:
            # Type can be narrowed to tuple[int, str, int].
            reveal_type(val)  # tuple[int, str, int]

This property may also be used to safely narrow tuple types within a ``match``
statement that uses sequence patterns.

If a tuple element is a union type, the tuple can be safely expanded into a
union of tuples. For example, ``tuple[int | str]`` is equivalent to
``tuple[int] | tuple[str]``. If multiple elements are union types, full expansion
must consider all combinations. For example, ``tuple[int | str, int | str]`` is
equivalent to ``tuple[int, int] | tuple[int, str] | tuple[str, int] | tuple[str, str]``.
Unbounded tuples cannot be expanded in this manner.

Type checkers may safely use this equivalency rule when narrowing tuple types::

    def func(subj: tuple[int | str, int | str]):
        match subj:
            case x, str():
                reveal_type(subj)  # tuple[int | str, str]
            case y:
                reveal_type(subj)  # tuple[int | str, int]

The ``tuple`` class derives from ``Sequence[T_co]`` where ``T_co`` is a covariant
(non-variadic) type variable. The specialized type of ``T_co`` should be computed
by a type checker as a supertype of all element types.
For example, ``tuple[int, *tuple[str, ...]]`` is a subtype of
``Sequence[int | str]`` or ``Sequence[object]``.

A zero-length tuple (``tuple[()]``) is a subtype of ``Sequence[Never]``.
