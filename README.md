[![Chat at https://gitter.im/python/typing](https://badges.gitter.im/python/typing.svg)](https://gitter.im/python/typing?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Static Typing for Python
========================

Documentation and Support
-------------------------

The documentation for Python's static typing can be found at
[typing.readthedocs.io](https://typing.readthedocs.io/). You can get
help either in our [support forum](/python/typing/discussions) or
chat with us on (Gitter)[https://gitter.im/python/typing].

Improvements to the type system should be discussed on the
[typing-sig](https://mail.python.org/mailman3/lists/typing-sig.python.org/)
mailing list, although the [issues](/python/typing/issues) in this
repository contain some historic discussions.

Repository Content
------------------

This GitHub repo is used for several things:

- A backport of the `typing` module for older Python versions (2.7 and
  3.4) is maintained in the [src directory](./src).
  Note that the canonical source lives
  [upstream](https://github.com/python/cpython/blob/master/Lib/typing.py)
  in the CPython repo.

- The `typing_extensions` module lives in the
  [typing\_extensions](./typing_extensions) directory.

- The documentation at [typing.readthedocs.io](https://typing.readthedocs.io/)
  is maintained in the [docs directory](./docs).

- A [discussion forum](/python/typing/discussions) for typing-related user
  help is hosted here.

Workflow
--------

* See [CONTRIBUTING.md](/CONTRIBUTING.md) for more.

* The typing.py module and its unittests are edited in the `src`
  subdirectory of this repo. The `python2` subdirectory contains the
  Python 2 backport.
