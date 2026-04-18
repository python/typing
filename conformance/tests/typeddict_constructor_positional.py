from typing import TypedDict

class TD1(TypedDict):
    a: int

class TD2(TD1):
    b: str

# keyword arguments (OK)
TD1(a=1)

# positional TypedDict (OK)
td2: TD2 = {"a": 1, "b": "x"}
TD1(td2)

# additional positional forms (behavior may vary across type checkers)
TD1({"a": 1})
TD1([("a", 1)])
