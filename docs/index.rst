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

* `PEP 482 <https://www.python.org/dev/peps/pep-0482/>`_, literature overview on type hints
* `PEP 483 <https://www.python.org/dev/peps/pep-0483/>`_, background on type hints
* `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_, type hints
* `PEP 526 <https://www.python.org/dev/peps/pep-0526/>`_, variable annotations and ``ClassVar``
* `PEP 544 <https://www.python.org/dev/peps/pep-0544/>`_, ``Protocol``
* `PEP 561 <https://www.python.org/dev/peps/pep-0561/>`_, distributing typed packages
* `PEP 563 <https://www.python.org/dev/peps/pep-0563/>`_, ``from __future__ import annotations``
* `PEP 585 <https://www.python.org/dev/peps/pep-0585/>`_, subscriptable generics in the standard library
* `PEP 586 <https://www.python.org/dev/peps/pep-0586/>`_, ``Literal``
* `PEP 589 <https://www.python.org/dev/peps/pep-0589/>`_, ``TypedDict``
* `PEP 591 <https://www.python.org/dev/peps/pep-0591/>`_, ``Final``
* `PEP 593 <https://www.python.org/dev/peps/pep-0593/>`_, ``Annotated``
* `PEP 604 <https://www.python.org/dev/peps/pep-0604/>`_, union syntax with ``|``
* `PEP 612 <https://www.python.org/dev/peps/pep-0612/>`_, ``ParamSpec``
* `PEP 613 <https://www.python.org/dev/peps/pep-0613/>`_, ``TypeAlias``
* `PEP 646 <https://www.python.org/dev/peps/pep-0646/>`_, variadic generics and ``TypeVarTuple``
* `PEP 647 <https://www.python.org/dev/peps/pep-0647/>`_, ``TypeGuard``
* `PEP 649 <https://www.python.org/dev/peps/pep-0649/>`_ (draft), ``from __future__ import co_annotations``
* `PEP 655 <https://www.python.org/dev/peps/pep-0655/>`_, ``Required`` and ``NotRequired``
* `PEP 673 <https://www.python.org/dev/peps/pep-0673/>`_, ``Self``
* `PEP 675 <https://www.python.org/dev/peps/pep-0675/>`_, ``LiteralString``
* `PEP 677 <https://www.python.org/dev/peps/pep-0677/>`_ (rejected), ``(int, str) -> bool`` callable type syntax
* `PEP 681 <https://www.python.org/dev/peps/pep-0681/>`_ ``@dataclass_transform()``
* `PEP 688 <https://www.python.org/dev/peps/pep-0688/>`_ ``Buffer``
* `PEP 692 <https://www.python.org/dev/peps/pep-0692/>`_ ``Unpack[TypedDict]`` for ``**kwargs``
* `PEP 695 <https://www.python.org/dev/peps/pep-0695/>`_ ``class Class[T]:`` type parameter syntax
* `PEP 696 <https://www.python.org/dev/peps/pep-0696/>`_ (draft), defaults for type variables
* `PEP 698 <https://www.python.org/dev/peps/pep-0698/>`_ ``@override``
* `PEP 702 <https://www.python.org/dev/peps/pep-0702/>`_ (draft), ``@deprecated()``
* `PEP 705 <https://www.python.org/dev/peps/pep-0705/>`_ (draft), ``TypedMapping``
