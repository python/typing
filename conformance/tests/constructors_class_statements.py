"""
Tests the evaluation of the implied metaclass call performed by class
statements.
"""

from typing import Any, assert_type

# Specification: https://typing.readthedocs.io/en/latest/spec/constructors.html#class-statements

# > Type checkers may report an error for a class statement whose base classes
# > have incompatible metaclasses.


class MetaA(type):
    pass


class MetaB(type):
    pass


class BaseA(metaclass=MetaA):
    pass


class BaseB(metaclass=MetaB):
    pass


class ClassConflict(BaseA, BaseB):  # E?: metaclass conflict
    pass


# > Type checkers should validate keyword arguments in a class statement's
# > argument list (other than ``metaclass``) by evaluating the implied
# > metaclass call using the constructor call rules described in
# > :ref:`constructor-calls`.


class Meta1(type):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        key: int,
    ):
        return super().__new__(mcls, name, bases, namespace)


class Class1(metaclass=Meta1, key=3):  # OK
    pass


class Class2(metaclass=Meta1, key=""):  # E: wrong type for "key"
    pass


class Class3(metaclass=Meta1):  # E: missing keyword argument "key"
    pass


# > Keyword arguments in a direct metaclass call (such as the last two calls
# > in the example above) require no special handling: they are validated as
# > part of evaluating the call using the standard constructor call rules.

Meta1("Class4", (), {}, key=3)  # OK
Meta1("Class5", (), {}, key="")  # E: wrong type for "key"


# > Type checkers should honor the evaluated return type of the implied
# > metaclass call, even if the evaluated type isn't a class.


class Meta2(type):
    def __new__(mcls, *args: object, **kwargs: object) -> int:
        return 1


class Class6(metaclass=Meta2):
    pass


assert_type(Class6, int)


# > Type checkers may validate the implied call to __prepare__().


class Meta3(type):
    @classmethod
    def __prepare__(  # E?: incompatible override of type.__prepare__() (out of scope for this test)
        mcls, name: str, bases: tuple[type, ...]
    ):  # No **kwds
        return {}

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        key: int,
    ):
        return super().__new__(mcls, name, bases, namespace)


class Class7(metaclass=Meta3, key=3):  # E?: "key" is not accepted by __prepare__()
    pass
