=================
Typing Extensions
=================

.. image:: https://badges.gitter.im/python/typing.svg
 :alt: Chat at https://gitter.im/python/typing
 :target: https://gitter.im/python/typing?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

Overview
========

The ``typing_extensions`` module serves two related purposes:

- Enable use of new type system features on older Python versions. For example,
  ``typing.TypeGuard`` is new in Python 3.10, but ``typing_extensions`` allows
  users on Python 3.6 through 3.9 to use it too.
- Enable experimentation with new type system PEPs before they are accepted and
  added to the ``typing`` module.
  
New features may be added to ``typing_extensions`` as soon as they are specified
in a PEP that has been added to the `python/peps <https://github.com/python/peps>`_
repository. If the PEP is accepted, the feature will then be added to ``typing``
for the next CPython release. No typing PEP has been rejected so far, so we
haven't yet figured out how to deal with that possibility.

Starting with version 4.0.0, ``typing_extensions`` uses
`Semantic Versioning <https://semver.org/>`_. The
major version is incremented for all backwards-incompatible changes.
Therefore, it's safe to depend
on ``typing_extensions`` like this: ``typing_extensions >=x.y, <(x+1)``,
where ``x.y`` is the first version that includes all features you need.

Included items
==============

This module currently contains the following:

- Experimental features

  - ``NotRequired`` (see PEP 655)
  - ``Required`` (see PEP 655)
  - ``Self`` (see PEP 673)

- In ``typing`` since Python 3.10
  
  - ``Concatenate`` (see PEP 612)
  - ``ParamSpec`` (see PEP 612)
  - ``ParamSpecArgs`` (see PEP 612)
  - ``ParamSpecKwargs`` (see PEP 612)
  - ``TypeAlias`` (see PEP 613)
  - ``TypeGuard`` (see PEP 647)

- In ``typing`` since Python 3.9

  - ``Annotated`` (see PEP 593)

- In ``typing`` since Python 3.8

  - ``final`` (see PEP 591)
  - ``Final`` (see PEP 591)
  - ``Literal`` (see PEP 586)
  - ``Protocol`` (see PEP 544)
  - ``runtime_checkable`` (see PEP 544)
  - ``TypedDict`` (see PEP 589)
  - ``get_origin`` (``typing_extensions`` provides this function only in Python 3.7+)
  - ``get_args`` (``typing_extensions`` provides this function only in Python 3.7+)

- In ``typing`` since Python 3.7

  - ``OrderedDict``

- In ``typing`` since Python 3.5 or 3.6 (see `the typing documentation
  <https://docs.python.org/3.10/library/typing.html>`_ for details)

  - ``AsyncContextManager``
  - ``AsyncGenerator``
  - ``AsyncIterable``
  - ``AsyncIterator``
  - ``Awaitable``
  - ``ChainMap``
  - ``ClassVar`` (see PEP 526)
  - ``ContextManager``
  - ``Coroutine``
  - ``Counter``
  - ``DefaultDict``
  - ``Deque``
  - ``NewType``
  - ``NoReturn``
  - ``overload``
  - ``Text``
  - ``Type``
  - ``TYPE_CHECKING``
  - ``get_type_hints`` (``typing_extensions`` provides this function only in Python 3.7+)

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
