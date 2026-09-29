"""
Tests the validation of class statement keyword arguments against the
``__init_subclass__`` method of the parent class.
"""

from typing import Any

# Specification: https://typing.readthedocs.io/en/latest/spec/constructors.html#the-init-subclass-method

# > If the metaclass of the class being defined does not define its own
# > __new__() method (including when no explicit metaclass is specified),
# > type checkers should validate the keyword arguments in a class statement's
# > argument list against the __init_subclass__() method of the parent
# > class.


class Base:
    def __init_subclass__(cls, *, flag: bool = False) -> None:
        super().__init_subclass__()


class Class1(Base, flag=True):  # OK
    pass


class Class2(Base, flag=""):  # E: wrong type for "flag"
    pass


class Class3(Base, other=1):  # E: no parameter named "other"
    pass


class Class4(other=1):  # E: object.__init_subclass__() accepts no keyword arguments
    pass


# > A metaclass __init__() method has no effect on this rule: when the
# > metaclass does not define its own __new__() method, type.__new__()
# > still forwards the keyword arguments to __init_subclass__(), so the
# > keyword arguments should satisfy both the metaclass __init__() method
# > (as part of validating the implied metaclass call) and the
# > __init_subclass__() method of the parent class.


class MetaInit(type):
    def __init__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        key: int,
    ) -> None:
        super().__init__(name, bases, namespace)


class Class5(Base, metaclass=MetaInit, key=1):  # E: "key" is not accepted by Base.__init_subclass__()
    pass


# > The same forwarding occurs when the metaclass is called directly ...
# > Type checkers may validate keyword arguments in such calls against the
# > __init_subclass__() method of the parent class when the base classes can
# > be statically determined.

type("ClassD", (Base,), {}, flag=True)  # OK
type("ClassE", (Base,), {}, other=1)  # E?: no parameter named "other"


# > If the metaclass defines its own __new__() method that accepts keyword
# > arguments only through a **kwargs parameter, whether these arguments
# > are forwarded to type.__new__() (and from there to
# > __init_subclass__()) cannot generally be determined statically. In this
# > situation, type checkers may additionally validate the keyword arguments
# > against the __init_subclass__() method of the parent class.


class MetaKwargs(type):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ):
        return super().__new__(mcls, name, bases, namespace, **kwargs)


class Class6(Base, metaclass=MetaKwargs, flag=True):  # OK
    pass


class Class7(Base, metaclass=MetaKwargs, other=1):  # E?: no parameter named "other"
    pass
