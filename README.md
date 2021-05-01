[![Chat at https://gitter.im/python/typing](https://badges.gitter.im/python/typing.svg)](https://gitter.im/python/typing?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

PEP 484: Type Hints
===================

This GitHub repo is used for three separate things:

- The issue tracker is used to discuss PEP-level type system issues.
  However,
  [typing-sig](https://mail.python.org/mailman3/lists/typing-sig.python.org/)
  is more appropriate these days.

- A backport of the `typing` module for older Python versions (2.7 and
  3.4) is maintained here.  Note that the canonical source lives
  [upstream](https://github.com/python/cpython/blob/master/Lib/typing.py)
  in the CPython repo.

- The `typing_extensions` module lives here.

Workflow
--------

* See [CONTRIBUTING.md](/CONTRIBUTING.md) for more.

* The typing.py module and its unittests are edited in the `src`
  subdirectory of this repo. The `python2` subdirectory contains the
  Python 2 backport.
