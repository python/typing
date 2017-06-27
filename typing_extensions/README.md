# Typing Extensions

The `typing_extensions` module contains backports of recent changes
to the `typing` module that were not present in older versions of
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

### Python 2 tests

To test Python 2, you should:

1. Install the latest version of typing
2. Navigate into `src_py2` and run `test_typing_extensions.py`

### Python 3 tests

Similarly, to test Python 3, you can:

1. Install the latest version of typing (for Python 3.4 or under)
2. Navigate into `src_py3` and run `test_typing_extensions.py`

However, you would need to repeat this test for each version of Python 3
that has been released since Python 3.5.0 for full coverage.

Since installing 7+ different versions of Python 3 is an onerous requirement,
this module provides a second way of running tests that requires you to only
have the latest version of Python 3 installed on your system:

- Run `py -3 run_tests.py` (for Windows)
- Run `python3 run_tests.py` (for Linux)

The `run_tests.py` file will essentially "modify" the standard library by
changing `PYTHONPATH` to point to individual folders in the `test_data` repo.

Each individual folder contains a snapshot of the source code for the 
`collections`, `typing,` and `abc` modules for that given release, letting us
test `typing` against those particular implementations.
