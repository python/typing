"""
Tests validation of frozen dataclass instances.
"""

# Specification: https://peps.python.org/pep-0557/#frozen-instances

from dataclasses import dataclass

@dataclass(frozen=True)
class DC1:
    a: float
    b: str

dc1 = DC1(1, "")

dc1.a = 1  # Type error: dataclass is frozen
dc1.b = "" # Type error: dataclass is frozen


# This should generate an error because a non-frozen dataclass
# cannot inherit from a frozen dataclass.
@dataclass
class DC2(DC1):
    pass

@dataclass
class DC3:
    a: int

# This should generate an error because a frozen dataclass
# cannot inherit from a non-frozen dataclass.
@dataclass(frozen=True)
class DC4(DC3):
    pass


@dataclass(frozen=True)
class DC1Child(DC1):
    # This should be allowed because attributes within a frozen
    # dataclass are covariant rather than invariant.
    a: int

