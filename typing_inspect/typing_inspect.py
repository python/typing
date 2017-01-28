"""Defines experimental API for runtime inspection of types defined
in the standard "typing" module.

Example usage::
    from typing_inspect import is_generic
"""

# NOTE: This module must support Python 2.7 in addition to Python 3.x

from typing import Callable, Union, Tuple, TypeVar, _gorg, ClassVar, Generic


def is_generic_type(tp):
    """Test if the given type is a generic type. This includes Generic itself, but
    excludes special typing constructs such as Union, Tuple, Callable, ClassVar.
    Examples::

        is_generic_type(int) == False
        is_generic_type(Union[int, str]) == False
        is_generic_type(Union[int, T]) == False
        is_generic_type(ClassVar[List[int]]) == False
        is_generic_type(Callable[..., T]) == False

        is_generic_type(Generic) == True
        is_generic_type(Generic[T]) == True
        is_generic_type(Iterable[int]) == True
        is_generic_type(Mapping) == True
        is_generic_type(MutableMapping[T, List[int]]) == True
        is_generic_type(Sequence[Union[str, bytes]]) == True
    """

    return type(tp) is type(Generic)


def is_callable_type(tp):
    """Test if the type is a generic callable type. Examples::

        is_callable_type(int) == False
        is_callable_type(type) == False
        is_callable_type(Callable) == True
        is_callable_type(Callable[..., int]) == True
        is_callable_type(Callable[[int, int], Iterable[str]]) == True
    """

    return type(tp) is type(Callable)


def is_tuple_type(tp):
    """Test if the type is a generic tuple type. Examples::

        is_tuple_type(int) == False
        is_tuple_type(tuple) == False
        is_tuple_type(Tuple) == True
        is_tuple_type(Tuple[str, int]) == True
    """

    return type(tp) is type(Tuple)


def is_union_type(tp):
    """Test if the type is a union type. Examples::

        is_union_type(int) == False
        is_union_type(Union) == True
        is_union_type(Union[int, int]) == False
        is_union_type(Union[T, int]) == True
    """

    return type(tp) is type(Union)


def is_typevar(tp):
    """Test if the type represents a type variable. Examples::

        is_typevar(int) == False
        is_typevar(T) == True
        is_typevar(Union[T, int]) == False
    """

    return type(tp) is TypeVar


def is_classvar(tp):
    """Test if the type represents a class variable. Examples::

        is_classvar(int) == False
        is_classvar(ClassVar) == True
        is_classvar(ClassVar[int]) == True
        is_classvar(ClassVar[List[T]]) == True
    """

    return type(tp) is type(ClassVar)


def get_origin(tp):
    """Get the unsubscripted version of a type. Supports generic types, Union,
    Callable, and Tuple. Returns None for unsupported types. Examples::

        get_origin(int) == None
        get_origin(ClassVar[int]) == None
        get_origin(Generic) == Generic
        get_origin(Generic[T]) == Generic
        get_origin(Union[T, int]) == Union
        get_origin(List[Tuple[T, T]][int]) == List
    """

    if is_generic_type(tp):
        return _gorg(tp)
    if is_union_type(tp):
        return Union
    if is_callable_type(tp):
        return Callable
    if is_tuple_type(tp):
        return Tuple

    return None


def get_parameters(tp):
    """Return type parameters of a parameterizable type as a tuple
    in lexicographic order. Parameterizable types are generic types,
    unions, tuple types and callable types. Examples::

        get_parameters(int) == ()
        get_parameters(Generic) == ()
        get_parameters(Union) == ()
        get_parameters(List[int]) == ()

        get_parameters(Generic[T]) == (T,)
        get_parameters(Tuple[List[T], List[S]]) == (T, S)
        get_parameters(Union[S, Tuple[T, T]][int, U]) == (U,)
        get_parameters(Mapping[T, Tuple[S, T]]) == (T, S)
    """

    if (
        is_generic_type(tp) or is_union_type(tp) or
        is_callable_type(tp) or is_tuple_type(tp)
    ):
        return tp.__parameters__
    return ()


def get_last_args(tp):
    """Get last arguments of (multiply) subscripted type. Examples::

        get_last_args(int) == ()
        get_last_args(Union) == ()
        get_last_args(ClassVar[int]) == (int,)
        get_last_args(Union[T, int]) == (int,)
        get_last_args(Iterable[Tuple[T, S]][int, T]) == (int, T)
    """

    if is_classvar(tp):
        return (tp.__type__,)
    if is_generic_type(tp) or is_union_type(tp):
        return tp.__args__
    return ()


def _eval_args(args):
    """Internal helper for get_args."""
    res = []
    for arg in args:
        if not isinstance(arg, tuple):
            res.append(arg)
        elif is_callable_type(arg[0]):
            if len(arg) == 2:
                res.append(Callable[[], arg[1]])
            elif arg[1] is Ellipsis:
                res.append(Callable[..., arg[2]])
            else:
                res.append(Callable[list(arg[1:-1]), arg[-1]])
        else:
            res.append(type(arg[0]).__getitem__(arg[0], _eval_args(arg[1:])))
    return tuple(res)


def get_args(tp, evaluate=False):
    """Get type arguments with all substitutions performed. For unions,
    basic simplifications used by Union constructor are performed.
    If `evaluate` is False (default), report result as nested tuple, this matches
    the internal representation of types. If `evaluate` is True, then all
    type parameters are applied (this could be expensive). Examples::

        get_args(Union[int, Tuple[T, int]][str]) == (int, (Tuple, str, int))
        get_args(Union[int, Union[T, int], str][int]) == (int, str)
        get_args(int) == ()

        get_args(Dict[int, Tuple[T, T]][Optional[int]], evaluate=True) == \
                 (int, Tuple[Optional[int], Optional[int]])
    """

    if is_classvar(tp):
        return (tp.__type__,)
    if is_generic_type(tp) or is_union_type(tp):
        tree = tp._subs_tree()
        if isinstance(tree, tuple) and len(tree) > 1:
            if not evaluate:
                return tree[1:]
            return _eval_args(tree[1:])
    return ()
