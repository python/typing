"""
Tests variance of ParamSpec.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/generics.html#semantics


from typing import Callable, Generic, ParamSpec


class InvariantParamSpec[**InOutP]:
    a: Callable[InOutP, None]

in_out_obj: InvariantParamSpec[object] = InvariantParamSpec[int]()  # E
in_out_int: InvariantParamSpec[int] = InvariantParamSpec[object]()  # E


class ContravariantParamSpec[**InP]:
    def f(self, *args: InP.args, **kwargs: InP.kwargs): ...

in_obj: ContravariantParamSpec[object] = ContravariantParamSpec[int]()  # E
in_int: ContravariantParamSpec[int] = ContravariantParamSpec[object]()  # OK


class CovariantParamSpec[**OutP]:
    def f(self, fn: Callable[OutP, None]) -> None:
        raise NotImplementedError


out_int: CovariantParamSpec[int] = CovariantParamSpec[object]()  # E
out_obj: CovariantParamSpec[object] = CovariantParamSpec[int]()  # OK

# cases involving keyword-only, positional-only parameters, parameter names, defaults and differing callable arities
class Box[T]:
    t: T

    def __init__(self, t: T): ...


def f(a: int): ...
def kw(*, a: int): ...
def pos(a: int, /): ...
def default(a: int = 1): ...
def arity(a: int, b: str): ...


class InitP[**P]:  # contravariant
    def __init__(self, fn: Callable[P, None]): ...

    def usage(self) -> Callable[P, None]:
        """infer contravariance"""
        raise NotImplementedError


box = Box(InitP(f))

kw_p = InitP(kw)
box.t = kw_p  # OK
pos_p = InitP(pos)
box.t = pos_p  # OK
names_p = InitP(f)
_: InitP[int]() = names_p  # E
default_p = InitP(default)
box.t = default_p  # E
arity_p = InitP(arity)
box.t = arity_p  # E


class OutitP[**P]:  # covariant
    def __init__(self, fn: Callable[P, None]): ...

    def usage(self, fn: Callable[P, None]):
        """infer covariance"""


box = Box(OutitP(f))

kw_p = OutitP(kw)
box.t = kw_p  # E
pos_p = OutitP(pos)
box.t = pos_p  # E
names_p = OutitP(f)
_: OutitP[int]() = names_p  # OK
default_p = OutitP(default)
box.t = default_p  # OK
arity_p = OutitP(arity)
box.t = arity_p  # E


# old style
P = ParamSpec("InP")  # OK
InP = ParamSpec("InP", contravariant=True)  # OK
InvP1 = ParamSpec("InvP1", covariant=True, contravariant=True)  # E
InvP2 = ParamSpec("InvP1", covariant=True, infer_variance=True)  # E
InvP3 = ParamSpec("InvP1", contravariant=True, infer_variance=True)  # E

class InvariantParamSpecOld(Generic[P]):
    def f(self, fn: Callable[InP, None]) -> Callable[InP, None]:  # OK
        raise NotImplementedError

in_out_old: InvariantParamSpecOld[int]
in_out_old = InvariantParamSpecOld[int]()  # OK
in_out_old = InvariantParamSpecOld[bool]()  # E
in_out_old = InvariantParamSpecOld[object]()  # E

class ContravariantParamSpecOld(Generic[InP]):
    def in_f(self) -> Callable[InP, None]:  # OK
        raise NotImplementedError

    def out_f(self, fn: Callable[InP, None]) -> None:  # E
        raise NotImplementedError


in_obj_old: ContravariantParamSpecOld[object] = ContravariantParamSpecOld[int]()  # E
in_int_old: ContravariantParamSpecOld[int] = ContravariantParamSpecOld[object]()  # OK

OutP = ParamSpec("OutP", covariant=True)


class CovariantParamSpecOld(Generic[OutP]):
    def in_f(self) -> Callable[OutP, None]:  # E
        raise NotImplementedError
    def out_f(self, fn: Callable[OutP, None]) -> None:  # OK
        raise NotImplementedError


out_int_old: CovariantParamSpecOld[int] = CovariantParamSpecOld[object]()  # E
out_obj_old: CovariantParamSpecOld[object] = CovariantParamSpecOld[int]()  # OK
