Type narrowing
==============

Type checkers should narrow the types of expressions in
certain contexts. This behavior is currently largely unspecified.

TypeGuard
---------

(Originally specified in :pep:`647`.)

The symbol ``TypeGuard``, exported from the ``typing`` module, is a special form
that accepts a single type argument. It is used to annotate the return type of a
user-defined type guard function. Return statements within a type guard function
should return bool values, and type checkers should verify that all return paths
return a bool.

In all other respects, ``TypeGuard`` is a distinct type from bool. It is not a
subtype of bool. Therefore, ``Callable[..., TypeGuard[int]]`` is not assignable
to ``Callable[..., bool]``.

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
