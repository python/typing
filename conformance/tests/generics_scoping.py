# Specification: https://typing.readthedocs.io/en/latest/spec/generics.html#scoping-rules-for-type-variables

# TODO: write PEP 695 versions

from typing import TypeVar, Generic, Iterable, assert_type

# > A type variable used in a generic function could be inferred to represent
# > different types in the same code block.
T = TypeVar('T')

def fun_1(x: T) -> T: ...  # T here
def fun_2(x: T) -> T: ...  # and here could be different

assert_type(fun_1(1), int)
assert_type(fun_2('a'), str)

# > A type variable used in a method of a generic class that coincides
# > with one of the variables that parameterize this class is always bound
# > to that variable.

class MyClass(Generic[T]):
    def meth_1(self, x: T) -> T: ...  # T here
    def meth_2(self, x: T) -> T: ...  # and here are always the same

a: MyClass[int] = MyClass()
a.meth_1(1)
a.meth_2('a')  # Type error

# > A type variable used in a method that does not match any of the variables
# > that parameterize the class makes this method a generic function in that
# > variable.

S = TypeVar("S")

class Foo(Generic[T]):
    def method(self, x: T, y: S) -> S:
        ...

x: Foo[int] = Foo()
assert_type(x.method(0, "abc"), str)
assert_type(x.method(0, b"abc"), bytes)

# > Unbound type variables should not appear in the bodies of generic functions,
# > or in the class bodies apart from method definitions.

def fun_3(x: T) -> list[T]:
    y: list[T] = []  # OK
    z: list[S] = []  # Type error
    return y

class Bar(Generic[T]):
    an_attr: list[S] = []  # Type error

    def do_something(self, x: S) -> S:  # OK
        ...

# A generic class definition that appears inside a generic function
# should not use type variables that parameterize the generic function.

def fun_4(x: T) -> list[T]:
    a_list: list[T] = []  # OK

    class MyGeneric(Generic[T]):  # Type error
        ...

    return a_list

# > A generic class nested in another generic class cannot use the same type
# > variables. The scope of the type variables of the outer class
# > doesn't cover the inner one

class Outer(Generic[T]):
    class Bad(Iterable[T]):  # Type error
        ...
    class AlsoBad:
        x: list[T]  # Type error

    class Inner(Iterable[S]):  # OK
        ...
    attr: Inner[T]  # OK
