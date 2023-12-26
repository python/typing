"""
Tests basic handling of the dataclass factory.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/dataclasses.html
# Also, see https://peps.python.org/pep-0557/

from dataclasses import InitVar, dataclass, field
from typing import ClassVar, Protocol, assert_type


@dataclass(order=True)
class InventoryItem:
    x = 0
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand


v1 = InventoryItem("soap", 2.3)


class InventoryItemInitProto(Protocol):
    def __call__(
        self, name: str, unit_price: float, quantity_on_hand: int = ...
    ) -> None:
        ...


# Validate the type of the synthesized __init__ method.
x1: InventoryItemInitProto = v1.__init__

# Make sure the following additional methods were synthesized.
print(v1.__repr__)
print(v1.__eq__)
print(v1.__ne__)
print(v1.__lt__)
print(v1.__le__)
print(v1.__gt__)
print(v1.__ge__)

assert_type(v1.name, str)
assert_type(v1.unit_price, float)
assert_type(v1.quantity_on_hand, int)

v2 = InventoryItem("name")  # Type error: missing unit_price
v3 = InventoryItem("name", "price")  # Type error: incorrect type for unit_price
v4 = InventoryItem("name", 3.1, 3, 4)  # Type error: too many arguments


# > TypeError will be raised if a field without a default value follows a
# > field with a default value. This is true either when this occurs in a
# > single class, or as a result of class inheritance.
@dataclass
class DC1:
    a: int = 0
    b: int  # Error: field with no default cannot follow field with default.


@dataclass
class DC2:
    a: int = field(default=1)
    b: int  # Error: field with no default cannot follow field with default.

@dataclass
class DC3:
    a: InitVar[int] = 0
    b: int  # Error: field with no default cannot follow field with default.


@dataclass
class DC4:
    a: int = field(init=False)
    b: int


v5 = DC4(0)
v6 = DC4(0, 1)  # Type error: too many parameters


@dataclass
class DC5:
    a: int = field(default_factory=str)  # Type error: type mismatch

@dataclass
class DC6:
    a: ClassVar[int] = 0
    b: str

dc6 = DC6("")
assert_type(dc6.a, int)
assert_type(DC6.a, int)
assert_type(dc6.b, str)


