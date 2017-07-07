# Typing Extensions

The `typing_extensions` module contains backports of recent changes
to the `typing` module that are not present in older versions of
`typing`.

This module is intended to be used mainly by people who are using
Python 3.5+, where the `typing` module is a part of the standard
library and cannot be updated to the latest version on PyPi.

Users of other Python versions should continue to install and use
use the `typing` module from PyPi instead of using this one, unless
they are specifically writing code intended to be compatible with
multiple versions of Python.

## Backported items

This module contains the following backported items:

### All Python versions:

- `ClassVar`
- `Collection`
- `ContextManager`
- `Counter`
- `DefaultDict`
- `Deque`
- `NewType`
- `NoReturn`
- `overload` (note that older versions of `typing` only let you use `overload` in stubs)
- `Text`
- `Type`
- `TYPE_CHECKING`

### Python 3.3+ only:

- `ChainMap`

### Python 3.5+ only:

- `AsyncIterable`
- `AsyncIterator`
- `AsyncContextManager`
- `Awaitable`
- `Coroutine`

### Python 3.6+ only:

- `AsyncGenerator`

## Other Notes and Limitations

There are a few types who's interface was modified between different
versions of typing. For example, `typing.Sequence` was modified to
subclass `typing.Reversible` as of Python 3.5.3.

These changes are _not_ backported to prevent subtle compatibility
issues when mixing the differing implementations of modified classes.

## Running tests

To run tests, navigate into the appropriate source directory and run
`test_typing_extensions.py`. You will also need to install the latest
version of `typing` if you are using a version of Python that does not
include `typing` as a part of the standard library.

