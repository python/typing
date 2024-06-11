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
* `Developer forum <https://discuss.python.org/c/typing/32>`_
* `Developer mailing list (archived) <https://mail.python.org/archives/list/typing-sig@python.org/>`_

Typing-related Tools
====================

Type Checkers
-------------

* `mypy <http://mypy-lang.org/>`_, the reference implementation for type
  checkers.
* `pyre <https://pyre-check.org/>`_, a type checker written in OCaml and
  optimized for performance.
* `pyright <https://github.com/microsoft/pyright>`_, a type checker that
  emphasizes speed.
* `pytype <https://google.github.io/pytype/>`_, a type checker that
  checks and infers types for unannotated code.

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
* `ruff <https://astral.sh/ruff>`_, a linter built for speed, with support for
  most of the ``flake8-pyi`` rules.

Type-Hint and Stub Integration
------------------------------

* `autotyping <https://github.com/JelleZijlstra/autotyping>`_, a tool which
  infers simple types from their context and inserts them as inline type-hints.
* `merge-pyi
  <https://google.github.io/pytype/developers/tools.html#merge_pyi>`_,
  a thin wrapper around ``ApplyTypeAnnotationsVisitor`` from
  `libCST <https://libcst.readthedocs.io/en/latest/>`_ that integrates .pyi
  signatures as inline type-hints in Python source code.

Typing PEPs
===========

See https://peps.python.org/topic/typing for a list of all typing-related PEPs.
