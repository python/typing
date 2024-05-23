.. _`type-narrowing`:

Type narrowing
==============

Type checkers should narrow the types of expressions in
certain contexts. This behavior is currently largely unspecified.

.. _`typeguard`:

TypeGuard
---------

(Originally specified in :pep:`647`.)

The symbol ``TypeGuard``, exported from the ``typing`` module, is a :term:`special form`
that accepts a single type argument. It is used to annotate the return type of a
user-defined type guard function. Return statements within a type guard function
should return bool values, and type checkers should verify that all return paths
return a bool.

``TypeGuard`` is also valid as the return type of a callable, for example
in callback protocols and in the ``Callable`` :term:`special form`. In these
contexts, it is treated as a subtype of bool. For example, ``Callable[..., TypeGuard[int]]``
is assignable to ``Callable[..., bool]``.

When ``TypeGuard`` is used to annotate the return type of a function or
method that accepts at least one parameter, that function or method is
treated by type checkers as a user-defined type guard. The type argument
provided for ``TypeGuard`` indicates the type that has been validated by
the function.

User-defined type guards can be generic functions, as shown in this example:

::

    _T = TypeVar("_T")

    def is_two_element_tuple(val: Tuple[_T, ...]) -> TypeGuard[tuple[_T, _T]]:
        return len(val) == 2

    def func(names: tuple[str, ...]):
        if is_two_element_tuple(names):
            reveal_type(names)  # tuple[str, str]
        else:
            reveal_type(names)  # tuple[str, ...]


Type checkers should assume that type narrowing should be applied to the
expression that is passed as the first positional argument to a user-defined
type guard. If the type guard function accepts more than one argument, no
type narrowing is applied to those additional argument expressions.

If a type guard function is implemented as an instance method or class method,
the first positional argument maps to the second parameter (after "self" or
"cls").

Here are some examples of user-defined type guard functions that accept more
than one argument:

::

    def is_str_list(val: list[object], allow_empty: bool) -> TypeGuard[list[str]]:
        if len(val) == 0:
            return allow_empty
        return all(isinstance(x, str) for x in val)

    _T = TypeVar("_T")

    def is_set_of(val: set[Any], type: type[_T]) -> TypeGuard[Set[_T]]:
        return all(isinstance(x, type) for x in val)


The return type of a user-defined type guard function will normally refer to
a type that is strictly "narrower" than the type of the first argument (that
is, it's a more specific type that can be assigned to the more general type).
However, it is not required that the return type be strictly narrower. This
allows for cases like the example above where ``list[str]`` is not assignable
to ``list[object]``.

When a conditional statement includes a call to a user-defined type guard
function, and that function returns true, the expression passed as the first
positional argument to the type guard function should be assumed by a static
type checker to take on the type specified in the TypeGuard return type,
unless and until it is further narrowed within the conditional code block.

Some built-in type guards provide narrowing for both positive and negative
tests (in both the ``if`` and ``else`` clauses). For example, consider the
type guard for an expression of the form ``x is None``. If ``x`` has a type that
is a union of None and some other type, it will be narrowed to ``None`` in the
positive case and the other type in the negative case. User-defined type
guards apply narrowing only in the positive case (the ``if`` clause). The type
is not narrowed in the negative case.

::

    OneOrTwoStrs = tuple[str] | tuple[str, str]
    def func(val: OneOrTwoStrs):
        if is_two_element_tuple(val):
            reveal_type(val)  # tuple[str, str]
            ...
        else:
            reveal_type(val)   # OneOrTwoStrs
            ...

        if not is_two_element_tuple(val):
            reveal_type(val)   # OneOrTwoStrs
            ...
        else:
            reveal_type(val)  # tuple[str, str]
            ...

TypeIs
------

(Originally specified in :pep:`742`.)

The :term:`special form` ``TypeIs`` is similar in usage, behavior, and runtime
implementation as ``TypeGuard``.

``TypeIs`` accepts a single type argument and can be used as the return type
of a function. A function annotated as returning a ``TypeIs`` is called a
"type narrowing function". Type narrowing functions must return ``bool``
values, and the type checker should verify that all return paths return
``bool``.

Type narrowing functions must accept at least one positional argument. The type
narrowing behavior is applied to the first positional argument passed to
the function. The function may accept additional arguments, but they are
not affected by type narrowing. If a type narrowing function is implemented as
an instance method or class method, the first positional argument maps
to the second parameter (after ``self`` or ``cls``).

To specify the behavior of ``TypeIs``, we use the following terminology:

* I = ``TypeIs`` input type
* R = ``TypeIs`` return type
* A = Type of argument passed to type narrowing function (pre-narrowed)
* NP = Narrowed type (positive; used when ``TypeIs`` returned ``True``)
* NN = Narrowed type (negative; used when ``TypeIs`` returned ``False``)

  ::

    def narrower(x: I) -> TypeIs[R]: ...

    def func1(val: A):
        if narrower(val):
            assert_type(val, NP)
        else:
            assert_type(val, NN)

The return type ``R`` must be consistent with ``I``. The type checker should
emit an error if this condition is not met.

Formally, type *NP* should be narrowed to :math:`A \land R`,
the intersection of *A* and *R*, and type *NN* should be narrowed to
:math:`A \land \neg R`, the intersection of *A* and the complement of *R*.
In practice, the theoretic types for strict type guards cannot be expressed
precisely in the Python type system. Type checkers should fall back on
practical approximations of these types. As a rule of thumb, a type checker
should use the same type narrowing logic -- and get results that are consistent
with -- its handling of :py:func:`isinstance`. This guidance allows for changes
and improvements if the type system is extended in the future.

Type narrowing is applied in both the positive and negative case::

    from typing import TypeIs, assert_type

    def is_str(x: object) -> TypeIs[str]:
        return isinstance(x, str)

    def f(x: str | int) -> None:
        if is_str(x):
            assert_type(x, str)
        else:
            assert_type(x, int)

The final narrowed type may be narrower than **R**, due to the constraints of the
argument's previously-known type::

    from collections.abc import Awaitable
    from typing import Any, TypeIs, assert_type
    import inspect

    def isawaitable(x: object) -> TypeIs[Awaitable[Any]]:
        return inspect.isawaitable(x)

    def f(x: Awaitable[int] | int) -> None:
        if isawaitable(x):
            # Type checkers may also infer the more precise type
            # "Awaitable[int] | (int & Awaitable[Any])"
            assert_type(x, Awaitable[int])
        else:
            assert_type(x, int)

It is an error to narrow to a type that is not consistent with the input type::

    from typing import TypeIs

    def is_str(x: int) -> TypeIs[str]:  # Type checker error
        ...

``TypeIs`` is also valid as the return type of a callable, for example
in callback protocols and in the ``Callable`` :term:`special form`. In these
contexts, it is treated as a subtype of bool. For example, ``Callable[..., TypeIs[int]]``
is assignable to ``Callable[..., bool]``.

Unlike ``TypeGuard``, ``TypeIs`` is invariant in its argument type:
``TypeIs[B]`` is not a subtype of ``TypeIs[A]``,
even if ``B`` is a subtype of ``A``.
To see why, consider the following example::

    def takes_narrower(x: int | str, narrower: Callable[[object], TypeIs[int]]):
        if narrower(x):
            print(x + 1)  # x is an int
        else:
            print("Hello " + x)  # x is a str

    def is_bool(x: object) -> TypeIs[bool]:
        return isinstance(x, bool)

    takes_narrower(1, is_bool)  # Error: is_bool is not a TypeIs[int]

(Note that ``bool`` is a subtype of ``int``.)
This code fails at runtime, because the narrower returns ``False`` (1 is not a ``bool``)
and the ``else`` branch is taken in ``takes_narrower()``.
If the call ``takes_narrower(1, is_bool)`` was allowed, type checkers would fail to
detect this error.
