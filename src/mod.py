from typing import TypeVar, Generic

T = TypeVar('T')

class A(Generic[T]):
    pass

class B(Generic[T]):
    class A(Generic[T]):
        pass