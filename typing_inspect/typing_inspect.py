"""Defines experimental API for runtime inspection of types defined
in the standard "typing" module.

Example usage::
    from typing_inspect import is_generic
"""

# NOTE: This module must support Python 2.7 in addition to Python 3.x

import sys
from typing import (
    Callable, Union, Tuple, TypeVar, Type, Generic,
    GenericMeta, _gorg, _Union, _ClassVar,
)

def _eval_args(args):
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

def is_generic_type(tp):
    return isinstance(tp, GenericMeta)

def get_origin(tp):
    if is_generic_type(tp):
        return _gorg(tp)
    if is_union_type(tp):
        return Union
    return None

def is_callable_type(tp):
    return get_origin(tp) is Callable

def is_tuple_type(tp):
    return get_origin(tp) is Tuple

def is_union_type(tp):
    return type(tp) is _Union

def is_typevar(tp):
    return type(tp) is TypeVar

def is_classvar(tp):
    return type(tp) is _ClassVar

def get_parameters(tp):
    if is_generic_type(tp) or is_union_type(tp):
        return tp.__parameters__
    return ()

def get_last_args(tp):
    if is_classvar(tp):
        return (tp.__type__,)
    if is_generic_type(tp) or is_union_type(tp):
        return tp.__args__
    return ()

def get_args(tp, evaluate=False):
    if is_classvar(tp):
        return (tp.__type__,)
    if is_generic_type(tp) or is_union_type(tp):
        tree = tp._subs_tree()
        if isinstance(tree, tuple) and len(tree) > 1:
            if not evaluate:
                return tree[1:]
            return _eval_args(tree[1:]) 
    return ()
