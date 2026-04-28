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

InP = ParamSpec("InP", contravariant=True)


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
