"""
Tests the handling of forward references in type annotations.
"""

# > When a type hint contains names that have not been defined yet, that
# > definition may be expressed as a string literal, to be resolved later.


import types
from typing import assert_type


def func1(
    p1: "ClassA", p2: "list[ClassA]", p3: list["ClassA"], p4: list["int | ClassA"]
) -> None:
    assert_type(p1, ClassA)
    assert_type(p2, list[ClassA])
    assert_type(p3, list[ClassA])
    assert_type(p4, list[ClassA | int])


bad1: ClassA  # Type error: requires quotes
bad2: list[ClassA]  # Type error: requires quotes
bad3: "ClassA" | int  # Runtime error
bad4: int | "ClassA"  # Runtime error


class ClassA:
    ...


# > The string literal should contain a valid Python expression
# > should be a valid code object).

var1 = 1


# The following should all generate errors because they are not legal type
# expressions, despite being enclosed in quotes.
def invalid_annotations(
    p1: "eval(" ".join(map(chr, [105, 110, 116])))",
    p2: "[int, str]",
    p3: "(int, str)",
    p4: "[int for i in range(1)]",
    p5: "{}",
    p6: "(lambda : int)()",
    p7: "[int][0]",
    p8: "int if 1 < 3 else str",
    p9: "var1",
    p10: "True",
    p11: "1",
    p12: "-1",
    p13: "int or str",
    p14: 'f"int"',
    p15: "types",
):
    pass


# > It should evaluate without errors once the module has been fully loaded.
# > The local and global namespace in which it is evaluated should be the same
# > namespaces in which default arguments to the same function would be evaluated.


class ClassB:
    def method1(self) -> ClassB:  # Runtime error
        return ClassB()

    def method2(self) -> "ClassB":  # OK
        return ClassB()


class ClassC:
    ...


class ClassD:
    ClassC: "ClassC"  # OK

    ClassF: "ClassF"  # Type error: circular reference

    str: "str" = ""  # OK

    def int(self) -> None:  # OK
        ...

    x: "int" = 0  # OK

    y: int = 0  # Type error: Refers to local int, which isn't a legal type expression


assert_type(ClassD.str, str)
assert_type(ClassD.x, int)
