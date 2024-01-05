"""
Tests the typing.Final special form.
"""

from typing import ClassVar, Final, Literal, NamedTuple, assert_type

# Specification: https://typing.readthedocs.io/en/latest/spec/qualifiers.html#id1

ID1: Final[int] = 1

ID2: Final = 1
assert_type(ID2, Literal[1])

# > If the right hand side is omitted, there must be an explicit type argument to Final.

BAD1: Final  # Type error: missing assignment

BAD2: Final[str, int] = ""  # Type error: only one type argument allowed

# > There can be at most one final declaration per module or class for a given
# > attribute.

# > As self.id: Final = 1 (also optionally with a type in square brackets).
# > This is allowed only in __init__ methods, so that the final instance
# > attribute is assigned only once when an instance is created.


class ClassA:
    ID1: Final = 1

    # > In class bodies and stub files you can omit the right hand side and just
    # > write ID: Final[float]. If the right hand side is omitted, there must be
    # > an explicit type argument to Final.
    ID2: Final  # Type error: missing initialization

    # > A final attribute declared in a class body without an initializer must
    # > be initialized in the __init__ method (except in stub files):
    ID3: Final[int]  # Type error: missing initialization

    ID4: Final[int]  # OK because initialized in __init__

    ID5: Final[int] = 0

    ID6: Final[int]

    ID7: Final[int] = 0

    def __init__(self, cond: bool) -> None:
        self.id1: Final = 1
        self.id2: Final[int] = 1

        self.ID4 = 1

        self.ID5 = 0  # Type error: Already initialized

        if cond:
            self.ID6 = 1
        else:
            self.ID6 = 2

    def method1(self) -> None:
        self.id3: Final = 1  # Type error: not allowed outside of __init__ method.
        self.id4: Final[int] = 1  # Type error: not allowed outside of __init__ method.

        self.ID7 = 0  # Type error: cannot modify Final value

        self.ID7 += 1  # Type error: cannot modify Final value


RATE: Final = 3000
RATE = 300  # Type error: Cannot redefine Final value

# > There can’t be separate class-level and instance-level constants
# > with the same name.


class ClassB:
    DEFAULT_ID: Final = 0


ClassB.DEFAULT_ID = 0  # Type error: Cannot redefined value


# > A type checker should prevent final attributes from being overridden in a subclass:


class ClassC:
    BORDER_WIDTH: Final = 2.5

    __private: Final = 0


class ClassCChild(ClassC):
    BORDER_WIDTH = 2.5  # Type error: Cannot override Final value

    __private = 0  # OK


# > Type checkers should infer a final attribute that is initialized in a class
# > body as being a class variable. Variables should not be annotated with both
# > ClassVar and Final.


class ClassD:
    VALUE1: Final = 1

    VALUE2: ClassVar[Final] = 1  # Type error: Final cannot be used with ClassVar
    VALUE3: Final[ClassVar] = 1  # Type error: Final cannot be used with ClassVar


ClassD.VALUE1  # OK


# > Final may only be used as the outermost type in assignments or variable
# > annotations. Using it in any other position is an error. In particular,
# > Final can’t be used in annotations for function arguments.

x: list[Final[int]] = []  # Type error


def func1(x: Final[list[int]]) -> None:  # Type error
    ...


# > Type checkers should treat uses of a final name that was initialized with
# > a literal as if it was replaced by the literal. For example, the following
# > should be allowed:

X: Final = "x"
Y: Final = "y"
N = NamedTuple("N", [(X, int), (Y, int)])

N(x=3, y=4)  # OK
N(a=1)  # Type error
N(x="", y="")  # Type error


def func2() -> None:
    global ID1

    ID1 = 2 # Type error: cannot modify Final value

    x: Final = 3

    x += 1 # Type error: cannot modify Final value

    a = (x := 4)  # Type error: cannot modify Final value

    for x in [1, 2, 3]: # Type error: cannot modify Final value
        pass

    with open("FileName") as x: # Type error: cannot modify Final value
        pass

    (a, x) = (1, 2)  # Type error: cannot modify Final value
