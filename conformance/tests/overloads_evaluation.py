"""
Tests for evaluation of calls to overloaded functions.
"""

from typing import assert_type, overload


# > Step 1: Examine the argument list to determine the number of
# > positional and keyword arguments. Use this information to eliminate any
# > overload candidates that are not plausible based on their
# > input signatures.

# > - If no candidate overloads remain, generate an error and stop.

@overload
def num_args(x: int, y: str) -> int:
    ...

@overload
def num_args(x: str) -> str:
    ...

def num_args(x: int | str, y: str = "") -> int | str:
    return 1

num_args()  # E: no matching overload


# > - If only one candidate overload remains, it is the winning match. Evaluate
# >   it as if it were a non-overloaded function call and stop.

ret1 = num_args(1, "")
assert_type(ret1, int)

ret2 = num_args(1, 1)  # E: Literal[1] not assignable to str
assert_type(ret2, int)

ret3 = num_args("")
assert_type(ret3, str)

ret4 = num_args(1)  # E: Literal[1] not assignable to str
assert_type(ret4, str)


