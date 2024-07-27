"""
Tests the warnings.deprecated function.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/directives.html#deprecated
# See also https://peps.python.org/pep-0702/

# > Type checkers should produce a diagnostic whenever they encounter a usage of an object
# > marked as deprecated. [...] For deprecated classes and functions, this includes:

# > * `from` imports

from _directives_deprecated_pep702_example import Ham  # E: Use of deprecated class Ham
import _directives_deprecated_pep702_example as library

from typing_extensions import deprecated


# > * References through module, class, or instance attributes

library.norwegian_blue(1)  # E: Use of deprecated function norwegian_blue
map(library.norwegian_blue, [1, 2, 3])  # E: Use of deprecated function norwegian_blue


# > For deprecated overloads, this includes all calls that resolve to the deprecated overload.

library.foo(1)  # E: Use of deprecated overload for foo
library.foo("x")  # no error


ham = Ham()  # no error (already reported above)


# > Any syntax that indirectly triggers a call to the function.

spam = library.Spam()

_ = spam + 1  # E: Use of deprecated method Spam.__add__
spam += 1  # E: Use of deprecated method Spam.__add__

spam.greasy  # E: Use of deprecated property Spam.greasy
spam.shape  # no error

spam.shape = "cube"  # E: Use of deprecated property setter Spam.shape
spam.shape += "cube"  # E: Use of deprecated property setter Spam.shape


# > * Any usage of deprecated objects in their defining module


@deprecated("Deprecated")
def lorem() -> None: ...


ipsum = lorem()  # E: Use of deprecated function lorem


# > There are additional scenarios where deprecations could come into play.
# > For example, an object may implement a `typing.Protocol`,
# > but one of the methods required for protocol compliance is deprecated.
# > As scenarios such as this one appear complex and relatively unlikely to come up in practice,
# > this PEP does not mandate that type checkers detect them.

from typing import Protocol, override


class Fooable(Protocol):

    @deprecated("Deprecated")
    def foo(self) -> None: ...

    def bar(self) -> None: ...


class Fooer(Fooable):

    @override
    def foo(self) -> None:  # E?: Implementation of deprecated method foo
        ...

    def bar(self) -> None: ...


def foo_it(fooable: Fooable) -> None:
    fooable.foo()  # E: Use of deprecated method foo
    fooable.bar()


# https://github.com/python/typing/pull/1822#discussion_r1693991644

class Fooable2(Protocol):

    def foo(self) -> None: ...


class Concrete:

    @deprecated("Deprecated")
    def foo(self) -> None: ...


def take_fooable(f: Fooable2) -> None: ...


def caller(c: Concrete) -> None:
    take_fooable(c)  # E?: Concrete is a Fooable2, but only because of a deprecated method
