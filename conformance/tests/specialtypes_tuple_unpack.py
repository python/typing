"""
Tests support for unpacked tuples used in type annotations.
"""

# PEP 646 adds the notion of an unpacked tuple.
t1: tuple[int, *tuple[str]] = (1, "")  # OK
t1 = (1, "", "")  # Type error

t2: tuple[int, *tuple[str, ...]] = (1,)  # OK
t2 = (1, "")  # OK
t2 = (1, "", "")  # OK
t2 = (1, 1, "")  # Type error
t2 = (1, "", 1)  # Type error


t3: tuple[int, *tuple[str, ...], int] = (1, 2)  # OK
t3 = (1, "", 2)  # OK
t3 = (1, "", "", 2)  # OK
t3 = (1, "", "")  # Type error
t3 = (1, "", "", 1.2)  # Type error

t4: tuple[*tuple[str, ...], int] = (1,)  # OK
t4 = ("", 1)  # OK
t4 = ("", "", 1)  # OK
t4 = (1, "", 1)  # Type error
t4 = ("", "", 1.2)  # Type error

t5: tuple[*tuple[str], *tuple[int]]  # Type error: only one unpack is allowed
t6: tuple[*tuple[str, ...], *tuple[int, ...]]  # Type error: only one unpack is allowed


def func1(a: tuple[str, str]):
    t1: tuple[str, str, *tuple[int, ...]] = a  # OK
    t2: tuple[str, str, *tuple[int]] = a  # Type error
    t3: tuple[str, *tuple[str, ...]] = a  # OK
    t4: tuple[str, str, *tuple[str, ...]] = a  # OK
    t5: tuple[str, str, str, *tuple[str, ...]] = a  # Type error
    t6: tuple[str, *tuple[int, ...], str] = a  # OK
    t7: tuple[*tuple[str, ...], str] = a  # OK
    t8: tuple[*tuple[str, ...], str] = a  # OK
    t9: tuple[*tuple[str, ...], str, str, str] = a  # Type error
