"""
Tests variance of TypeVarTuple.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/generics.html#semantics


from typing import Generic, TypeVarTuple

class ContravariantTypeVarTuple[*InTs]:
    def f(self, t: tuple[*InTs]):
        raise NotImplementedError

in_obj: ContravariantTypeVarTuple[object] = ContravariantTypeVarTuple[int]()  # E
in_int: ContravariantTypeVarTuple[int] = ContravariantTypeVarTuple[object]()  # OK


class CovariantTypeVarTuple[*OutTs]:
    def f(self) -> tuple[*OutTs]:
        raise NotImplementedError


out_int: CovariantTypeVarTuple[int] = CovariantTypeVarTuple[object]()  # E
out_obj: CovariantTypeVarTuple[object] = CovariantTypeVarTuple[int]()  # OK


InTs = TypeVarTuple("InTs", contravariant=True)


class ContravariantTypeVarTupleOld(Generic[*InTs]):
    def in_f(self, *args: *InTs) -> None:  # OK
        raise NotImplementedError

    def out_f(self) -> tuple[*InTs]:  # E
        raise NotImplementedError


in_obj_old: ContravariantTypeVarTupleOld[object] = ContravariantTypeVarTupleOld[int]()  # E
in_int_old: ContravariantTypeVarTupleOld[int] = ContravariantTypeVarTupleOld[object]()  # OK

OutTs = TypeVarTuple("OutTs", covariant=True)


class CovariantTypeVarTupleOld(Generic[*OutTs]):
    def in_f(self, *args: *OutTs) -> None:  # E
        raise NotImplementedError

    def out_f(self) -> tuple[*OutTs]:  # OK
        raise NotImplementedError


out_int_old: CovariantTypeVarTupleOld[int] = CovariantTypeVarTupleOld[object]()  # E
out_obj_old: CovariantTypeVarTupleOld[object] = CovariantTypeVarTupleOld[int]()  # OK
