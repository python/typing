"""
Tests the warnings.deprecated function when it is used in a Protocol.
"""

# > There are additional scenarios where deprecations could come into play.
# > For example, an object may implement a `typing.Protocol`,
# > but one of the methods required for protocol compliance is deprecated.
# > As scenarios such as this one appear complex and relatively unlikely to come up in practice,
# > this PEP does not mandate that type checkers detect them.

from typing import Protocol

from typing_extensions import deprecated


class Fooable(Protocol):

    @deprecated("Deprecated")
    def foo(self) -> None: ...

    def bar(self) -> None: ...


class Fooer(Fooable):

    def foo(self) -> None:  # E?: Implementation of deprecated method foo
        ...

    def bar(self) -> None: ...


def foo_it(fooable: Fooable) -> None:
    fooable.foo()  # E: Use of deprecated method foo
    fooable.bar()
