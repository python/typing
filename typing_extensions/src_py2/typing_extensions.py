import abc
import collections
import typing
from typing import (
    ClassVar, Type,
    Counter, DefaultDict, Deque,
    NewType, overload, Text, TYPE_CHECKING,
)

# Please keep __all__ alphabetized within each category.
__all__ = [
    # Super-special typing primitives.
    'ClassVar',
    'Type',

    # Concrete collection types.
    'ContextManager',
    'Counter',
    'Deque',
    'DefaultDict',

    # One-off things.
    'NewType',
    'overload',
    'Text',
    'TYPE_CHECKING',
]


if hasattr(typing, 'NoReturn'):
    NoReturn = typing.NoReturn
else:
    # TODO: Remove once typing.py has been updated
    class NoReturnMeta(typing.TypingMeta):
        """Metaclass for NoReturn."""

        def __new__(cls, name, bases, namespace):
            cls.assert_no_subclassing(bases)
            self = super(NoReturnMeta, cls).__new__(cls, name, bases, namespace)
            return self

    class _NoReturn(typing._FinalTypingBase):
        """Special type indicating functions that never return.
        Example::
          from typing import NoReturn
          def stop() -> NoReturn:
              raise Exception('no way')
        This type is invalid in other positions, e.g., ``List[NoReturn]``
        will fail in static type checkers.
        """
        __metaclass__ = NoReturnMeta
        __slots__ = ()

        def __instancecheck__(self, obj):
            raise TypeError("NoReturn cannot be used with isinstance().")

        def __subclasscheck__(self, cls):
            raise TypeError("NoReturn cannot be used with issubclass().")

    NoReturn = _NoReturn(_root=True)


T_co = typing.TypeVar('T_co', covariant=True)

if hasattr(typing, 'ContextManager'):
    ContextManager = typing.ContextManager
else:
    # TODO: Remove once typing.py has been updated
    class ContextManager(typing.Generic[T_co]):
        __slots__ = ()

        def __enter__(self):
            return self

        @abc.abstractmethod
        def __exit__(self, exc_type, exc_value, traceback):
            return None

        @classmethod
        def __subclasshook__(cls, C):
            if cls is ContextManager:
                # In Python 3.6+, it is possible to set a method to None to
                # explicitly indicate that the class does not implement an ABC
                # (https://bugs.python.org/issue25958), but we do not support
                # that pattern here because this fallback class is only used
                # in Python 3.5 and earlier.
                if (any("__enter__" in B.__dict__ for B in C.__mro__) and
                    any("__exit__" in B.__dict__ for B in C.__mro__)):
                    return True
            return NotImplemented

