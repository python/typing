*************************
Static Typing with Python
*************************

.. Introduction
.. ============
..
.. .. toctree::
..    :maxdepth: 2
..
..    source/introduction

Guides
======

.. toctree::
   :maxdepth: 2

   source/guides

Reference
=========

.. toctree::
   :maxdepth: 2

   source/reference

.. seealso::

   The documentation at https://mypy.readthedocs.io/ is relatively accessible
   and complete. Particularly refer to the "Type System Reference" section of
   the docs -- since the Python typing system is standardised via PEPs, this
   information should apply to most Python type checkers.

Specification
=============

.. toctree::
   :maxdepth: 2

   spec/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _contact:

Discussions and Support
=======================

* `User help forum <https://github.com/python/typing/discussions>`_
* `User chat on Gitter <http://gitter.im/python/typing>`_
* `Developer mailing list <https://mail.python.org/archives/list/typing-sig@python.org/>`_

Typing-related Tools
====================

Type Checkers
-------------

* `mypy <http://mypy-lang.org/>`_, the reference implementation for type
  checkers.
* `pyre <https://pyre-check.org/>`_, written in OCaml and optimized for
  performance.
* `pyright <https://github.com/microsoft/pyright>`_, a type checker that
  emphasizes speed.
* `pytype <https://google.github.io/pytype/>`_, checks and infers types for
  unannotated code.

Development Environments
------------------------

* `PyCharm <https://www.jetbrains.com/pycharm/>`_, an IDE that supports
  type stubs both for type checking and code completion.
* `Visual Studio Code <https://code.visualstudio.com/>`_, a code editor that
  supports type checking using mypy, pyright, or the
  `Pylance <https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance>`_
  extension.

Linters and Formatters
----------------------

* `black <https://black.readthedocs.io/>`_, a code formatter with support for
  type stub files.
* `flake8-pyi <https://github.com/ambv/flake8-pyi>`_, a plugin for the
  `flake8 <https://flake8.pycqa.org/>`_ linter that adds support for type
  stubs.

Type-Hint and Stub Integration
------------------------------

* `autotyping <https://github.com/JelleZijlstra/autotyping>`_, a tool which infers simple types from their context and inserts them as inline type-hints.
* `merge_pyi <https://google.github.io/pytype/developers/tools.html#merge_pyi>`_, integrates .pyi signatures as inline type-hints in Python source code.
  This is a thin wrapper around ``ApplyTypeAnnotationsVisitor`` from `libCST <https://libcst.readthedocs.io/en/latest/>`_.

Typing PEPs
===========

https://peps.python.org/topic/typing

* :pep:`482`, literature overview on type hints
* :pep:`483`, background on type hints
* :pep:`484`, type hints
* :pep:`526`, variable annotations and ``ClassVar``
* :pep:`544`, ``Protocol``
* :pep:`561`, distributing typed packages
* :pep:`563` (superseded), ``from __future__ import annotations``
* :pep:`585`, subscriptable generics in the standard library
* :pep:`586`, ``Literal``
* :pep:`589`, ``TypedDict``
* :pep:`591`, ``Final``
* :pep:`593`, ``Annotated``
* :pep:`604`, union syntax with ``|``
* :pep:`612`, ``ParamSpec``
* :pep:`613`, ``TypeAlias``
* :pep:`646`, variadic generics and ``TypeVarTuple``
* :pep:`647`, ``TypeGuard``
* :pep:`649`, lazy evaluation of annotations
* :pep:`655`, ``Required`` and ``NotRequired``
* :pep:`673`, ``Self``
* :pep:`675`, ``LiteralString``
* :pep:`677` (rejected), ``(int, str) -> bool`` callable type syntax
* :pep:`681`, ``@dataclass_transform()``
* :pep:`688`, ``Buffer``
* :pep:`692`, ``Unpack[TypedDict]`` for ``**kwargs``
* :pep:`695`, ``class Class[T]:`` type parameter syntax and ``type X`` type alias syntax
* :pep:`696`, defaults for type variables
* :pep:`698`, ``@override``
* :pep:`702`, ``@deprecated()``
* :pep:`705`, ``TypedDict`` with read-only items
* :pep:`718` (draft), subscriptable functions
* :pep:`724` (withdrawn), stricter ``TypeGuard``
* :pep:`727` (draft), ``Doc`` in ``Annotated``
* :pep:`728` (draft), ``TypedDict`` with typed extra items
* :pep:`729`, typing governance process
* :pep:`742`, ``TypeIs``
