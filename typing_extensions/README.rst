=================
Typing Extensions
=================

.. image:: https://badges.gitter.im/python/typing.svg
 :alt: Chat at https://gitter.im/python/typing
 :target: https://gitter.im/python/typing?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

Overview
========

The ``typing_extensions`` module contains both backports of ``typing`` features
as well as experimental types that will eventually be added to the ``typing``
module, such as ``Protocol`` (see PEP 544 for details about protocols and
static duck typing) or ``TypedDict`` (see PEP 589).

Users of other Python versions should continue to install and use
the ``typing`` module from PyPi instead of using this one unless
specifically writing code that must be compatible with multiple Python
versions or requires experimental types.

Starting with version 4.0.0, ``typing_extensions`` uses
`Semantic Versioning <https://semver.org/>`_. The
major version is incremented for all backwards-incompatible changes, including
dropping support for older Python versions. Therefore, it's safe to depend
on ``typing_extensions`` like this: ``typing_extensions >=x.y, <(x+1)``,
where ``x.y`` is the first version that includes all features you need.

Included items
==============

This module currently contains the following:

- ``Annotated``
- ``AsyncContextManager``
- ``AsyncGenerator``
- ``AsyncIterable``
- ``AsyncIterator``
- ``Awaitable``
- ``ChainMap``
- ``ClassVar``
- ``Concatenate``
- ``ContextManager``
- ``Coroutine``
- ``Counter``
- ``DefaultDict``
- ``Deque``
- ``final``
- ``Final``
- ``Literal``
- ``NewType``
- ``NoReturn``
- ``overload`` (note that older versions of ``typing`` only let you use ``overload`` in stubs)
- ``OrderedDict``
- ``ParamSpec``
- ``ParamSpecArgs``
- ``ParamSpecKwargs``
- ``Protocol``
- ``runtime_checkable``
- ``Text``
- ``Type``
- ``TypedDict``
- ``TypeAlias``
- ``TypeGuard``
- ``TYPE_CHECKING``

Other Notes and Limitations
===========================

There are a few types whose interface was modified between different
versions of typing. For example, ``typing.Sequence`` was modified to
subclass ``typing.Reversible`` as of Python 3.5.3.

These changes are _not_ backported to prevent subtle compatibility
issues when mixing the differing implementations of modified classes.

Certain types have incorrect runtime behavior due to limitations of older
versions of the typing module.  For example, ``ParamSpec`` and ``Concatenate``
will not work with ``get_args``, ``get_origin``. Certain PEP 612 special cases
in user-defined ``Generic``\ s are also not available.
These types are only guaranteed to work for static type checking.

Running tests
=============

To run tests, navigate into the appropriate source directory and run
``test_typing_extensions.py``. You will also need to install the latest
version of ``typing`` if you are using a version of Python that does not
include ``typing`` as a part of the standard library.
