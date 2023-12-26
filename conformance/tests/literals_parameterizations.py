"""
Tests legal and illegal parameterizations of Literal.
"""

# > Literal must be parameterized with at least one type.

from typing import Any, Literal, TypeVar
from enum import Enum


class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2


good1: Literal[26]
good2: Literal[0x1A]
good3: Literal[-4]
good4: Literal["hello world"]
good5: Literal[b"hello world"]
good6: Literal["hello world"]
good7: Literal[True]
good8: Literal[Color.RED]
good9: Literal[None]

ReadOnlyMode = Literal["r", "r+"]
WriteAndTruncateMode = Literal["w", "w+", "wt", "w+t"]
WriteNoTruncateMode = Literal["r+", "r+t"]
AppendMode = Literal["a", "a+", "at", "a+t"]

AllModes = Literal[ReadOnlyMode, WriteAndTruncateMode, WriteNoTruncateMode, AppendMode]

good10: Literal[Literal[Literal[1, 2, 3], "foo"], 5, None]

variable = 3
T = TypeVar("T")

# > Arbitrary expressions [are illegal]
bad1: Literal[3 + 4]  # Type error
bad2: Literal["foo".replace("o", "b")]  # Type error
bad3: Literal[4 + 3j]  # Type error
bad4: Literal[+5]  # Type error
bad5: Literal[not False]  # Type error
bad6: Literal[(1, "foo", "bar")]  # Type error
bad7: Literal[{"a": "b", "c": "d"}]  # Type error
bad8: Literal[int]  # Type error
bad9: Literal[variable]  # Type error
bad10: Literal[T]  # Type error
bad11: Literal[3.14]  # Type error
bad12: Literal[Any]  # Type error
bad13: Literal[...]  # Type error


def my_function(x: Literal[1 + 2]) -> int:  # Type error
    return x * 3

x: Literal  # Type error
y: Literal[my_function] = my_function  # Type error


def func2(a: Literal[Color.RED]):
    x1: Literal["Color.RED"] = a  # Type error

    x2: "Literal[Color.RED]" = a  # OK


