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

There are two different ways to test this module. The first is to simply run
each individual Python interpreter against `test_typing_extensions.py` in the 
`src_py2` and `src_py3` folders.

However, because multiple versions of Python for each individual release
can be onerous, you can instead run `run_tests.py` using a single Python
interpreter. The `run_tests.py` file will essentially "modify" the standard
library by changing `PYTHONPATH` to point to individual folders in the 
`test_data` repo.

Each individual folder contains a snapshot of the source code for the 
`collections`, `typing,` and `abc` modules for that given release, letting us
test `typing` against those particular implementations.

`run_tests.py` will assume that you have Python 3.6.1 and a reasonably
modern version of Python 2.7 installed on your system, aliased to 
`py -2.7` and `py -3.6` on Windows, and `python` and `python3` on Linux and
Mac.
