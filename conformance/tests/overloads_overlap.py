"""
Tests checks for overlapping overloads.
"""

from typing import Literal, overload

# > If two overloads can accept the same set of arguments, they are said
# > to "partially overlap". If two overloads partially overlap, the return type
# > of the former overload should be assignable to the return type of the
# > latter overload. If this condition doesn't hold, it is indicative of a
# > programming error and should be reported by type checkers.

@overload
def is_one(x: Literal[1]) -> Literal[True]:  # E: overlapping overloads, inconsistent return type
    ...

@overload
def is_one(x: int) -> Literal[False]:
    ...

def is_one(x: int) -> bool:
    return x == 1
