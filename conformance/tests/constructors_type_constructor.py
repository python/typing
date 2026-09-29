"""
Tests the special-case handling of calls to the ``type`` constructor.
"""

from typing import assert_type

# Specification: https://typing.readthedocs.io/en/latest/spec/constructors.html#the-type-constructor

# > Although the single-argument form is typically declared with a return type
# > of `type`, type checkers should special-case this form and evaluate its
# > result as type[T], where T is the type of the argument.


def func1(x: int, y: int | str) -> None:
    assert_type(type(x), type[int])
    assert_type(type(y), type[int] | type[str])


# > At runtime, the single-argument form applies only when the class being
# > called is `type` itself, and is not inherited by metaclasses: a
# > single-argument call to a subclass of `type` raises a TypeError.


class Meta(type):
    pass


assert_type(type(1), type[int])  # OK, uses the single-argument form
Meta(1)  # E: single-argument form does not apply to subclasses
type("A", ())  # E: two-argument form does not exist

# > The evaluated return type of the three-argument form is an instance of the
# > metaclass being called ... Type checkers may infer a more precise type for
# > the returned class object.

meta_instance: Meta = Meta("A", (), {})  # OK, uses the three-argument form


# > This special-casing applies only to the __new__() and __init__()
# > methods inherited from `type`. If a metaclass defines its own
# > __new__() method that accepts a single argument, calls to it should be
# > evaluated using the rules for regular constructor calls described earlier
# > in this chapter.


class MetaSingle(type):
    def __new__(mcls, x: int):
        return super().__new__(mcls, "X", (), {})


MetaSingle(1)  # OK
MetaSingle("")  # E: wrong type for "x"
