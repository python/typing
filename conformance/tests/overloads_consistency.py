"""
Tests consistency of overloads with implementation.
"""

from typing import overload

# > If an overload implementation is defined, type checkers should validate
# > that it is consistent with all of its associated overload signatures.
# > The implementation should accept all potential sets of arguments
# > that are accepted by the overloads and should produce all potential return
# > types produced by the overloads. In typing terms, this means the input
# > signature of the implementation should be :term:<assignable> to the input
# > signatures of all overloads, and the return type of all overloads should be
# > assignable to the return type of the implementation.

# Return type of all overloads must be assignable to return type of
# implementation:

@overload
def return_type(x: int) -> int:
    ...

@overload
def return_type(x: str) -> str:  # E[return_type]
    ...

def return_type(x: int | str) -> int:  # E[return_type] an overload returns `str`, not assignable to `int`
    return 1


# Input signature of implementation must be assignable to signature of each
# overload:

@overload
def parameter_type(x: int) -> int:
    ...

@overload
def parameter_type(x: str) -> str:  # E[parameter_type]
    ...

def parameter_type(x: int) -> int | str:  # E[parameter_type] impl type of `x` must be assignable from overload types of `x`
    return 1
