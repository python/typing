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

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

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
  checkers. Supports Python 2 and 3.
* `pyre <https://pyre-check.org/>`_, written in OCaml and optimized for
  performance. Supports Python 3 only.
* `pyright <https://github.com/microsoft/pyright>`_, a type checker that
  emphasizes speed. Supports Python 3 only.
* `pytype <https://google.github.io/pytype/>`_, checks and infers types for
  unannotated code. Supports Python 2 and 3.

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

Typing PEPs
===========

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
* `PEP 655 <https://www.python.org/dev/peps/pep-0655/>`_, ``Required`` and ``NotRequired``
* `PEP 673 <https://www.python.org/dev/peps/pep-0673/>`_, ``Self``
* `PEP 675 <https://www.python.org/dev/peps/pep-0675/>`_, ``LiteralString``
* `PEP 677 <https://www.python.org/dev/peps/pep-0677/>`_ (rejected), callable type syntax
* `PEP 681 <https://www.python.org/dev/peps/pep-0681/>`_ (draft), ``@dataclass_transform()``
