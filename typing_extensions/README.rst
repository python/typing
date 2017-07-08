=================
Typing Extensions
=================

.. image:: https://badges.gitter.im/python/typing.svg
 :alt: Chat at https://gitter.im/python/typing
 :target: https://gitter.im/python/typing?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

Overview
========

The ``typing_extensions`` module contains both backports of changes made to
the ``typing`` module since Python 3.5.0 as well as experimental types that
will be eventually added to the ``typing`` module once stabilized.

This module is intended to be used by people who:

1. Are using Python 3.5+ and cannot upgrade to newer versions of Python.
   Since the ``typing`` module was (provisionally) added to the Python standard
   library in 3.5, users who are unable to upgrade cannot take advantage of
   new additions to typing such as ``typing.Text`` or ``typing.Coroutine``.
2. Are interested in using experimental additions to the ``typing`` module.

Users of other Python versions should continue to install and use
use the ``typing`` module from PyPi instead of using this one unless
specifically writing code that must be compatible with multiple Python
versions or requires experimental types.

Included items
==============

This module currently contains the following:

All Python versions:
--------------------

- ``ClassVar``
- ``ContextManager``
- ``Counter``
- ``DefaultDict``
- ``Deque``
- ``NewType``
- ``NoReturn``
- ``overload`` (note that older versions of ``typing`` only let you use ``overload`` in stubs)
- ``Text``
- ``Type``
- ``TYPE_CHECKING``

Python 3.3+ only:
-----------------

- ``ChainMap``

Python 3.5+ only:
-----------------

- ``AsyncIterable``
- ``AsyncIterator``
- ``AsyncContextManager``
- ``Awaitable``
- ``Coroutine``

Python 3.6+ only:
-----------------

- ``AsyncGenerator``

Other Notes and Limitations
===========================

There are a few types whose interface was modified between different
versions of typing. For example, ``typing.Sequence`` was modified to
subclass ``typing.Reversible`` as of Python 3.5.3.

These changes are _not_ backported to prevent subtle compatibility
issues when mixing the differing implementations of modified classes.

Running tests
=============

To run tests, navigate into the appropriate source directory and run
``test_typing_extensions.py``. You will also need to install the latest
version of ``typing`` if you are using a version of Python that does not
include ``typing`` as a part of the standard library.

