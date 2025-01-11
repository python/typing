"""
Tests for evaluation of calls to overloaded functions.
"""

from typing import assert_type, overload


# > Step 1: Examine the argument list to determine the number of
# > positional and keyword arguments. Use this information to eliminate any
# > overload candidates that are not plausible based on their
# > input signatures.

@overload
def example1(x: int, y: str) -> int:
    ...

@overload
def example1(x: str) -> str:
    ...

def example1(x: int | str, y: str = "") -> int | str:
    return 1

# > - If no candidate overloads remain, generate an error and stop.

example1()  # E: no matching overload

# > - If only one candidate overload remains, it is the winning match. Evaluate
# >   it as if it were a non-overloaded function call and stop.

ret1 = example1(1, "")
assert_type(ret1, int)

ret2 = example1(1, 1)  # E: Literal[1] not assignable to str
assert_type(ret2, int)

ret3 = example1("")
assert_type(ret3, str)

ret4 = example1(1)  # E: Literal[1] not assignable to str
assert_type(ret4, str)


# > Step 2: Evaluate each remaining overload as a regular (non-overloaded)
# > call to determine whether it is compatible with the supplied
# > argument list. Unlike step 1, this step considers the types of the parameters
# > and arguments. During this step, do not generate any user-visible errors.
# > Simply record which of the overloads result in evaluation errors.

@overload
def example2(x: int, y: str, z: int) -> str:
    ...

@overload
def example2(x: int, y: int, z: int) -> int:
    ...

def example2(x: int, y: int | str, z: int) -> int | str:
    return 1

# > - If only one overload evaluates without error, it is the winning match.
# >   Evaluate it as if it were a non-overloaded function call and stop.

ret5 = example2(1, 2, 3)
assert_type(ret5, int)

# > Step 3: If step 2 produces errors for all overloads, perform
# > "argument type expansion". Union types can be expanded
# > into their constituent subtypes. For example, the type ``int | str`` can
# > be expanded into ``int`` and ``str``.

# > - If all argument lists evaluate successfully, combine their
# >   respective return types by union to determine the final return type
# >   for the call, and stop.

def _(v: int | str) -> None:
    ret1 = example2(1, v, 1)
    assert_type(ret1, int | str)

# > - If argument expansion has been applied to all arguments and one or
# >   more of the expanded argument lists cannot be evaluated successfully,
# >   generate an error and stop.

def _(v: int | str) -> None:
    example2(v, v, 1)  # E: no overload matches (str, ..., ...)

