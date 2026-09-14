"""
Tests the handling name-resolution in annotations while from __future__ import
annotations is present.
"""

from __future__ import annotations

from typing import assert_type

# > For purposes of type checking, annotations in a file containing from
# > __future__ import annotations must use the same name-resolution rules as
# > explicitly stringified annotations, regardless of the target Python version.

forward1: ClassA
forward2: list[ClassA]
forward3: "ClassA"


class ClassA:
    ...


class ClassB:
    ClassA: ClassA
    ClassC: ClassC
    inner1: ClassInner
    inner2: "ClassInner"

    class ClassInner:
        ...

    inner_after1: ClassInner
    inner_after2: "ClassInner"


class ClassC:
    ...


def check_valid_attributes(b: ClassB) -> None:
    assert_type(b.ClassC, ClassC)
    assert_type(b.inner1, ClassB.ClassInner)
    assert_type(b.inner2, ClassB.ClassInner)
    assert_type(b.inner_after1, ClassB.ClassInner)
    assert_type(b.inner_after2, ClassB.ClassInner)
