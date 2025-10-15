*************************
Static Typing with Python
*************************

Tutorials
=========

..
   Keep in sync with tutorials/index.rst.

.. toctree::
   :maxdepth: 1

   tutorials/external_libraries

Guides
======

..
   Keep in sync with docs/guides/index.rst.

.. toctree::
   :maxdepth: 1

   guides/libraries
   guides/writing_stubs
   guides/modernizing
   guides/unreachable
   guides/type_narrowing
   guides/typing_anti_pitch

Reference
=========

..
   Keep in sync with docs/reference/index.rst.

.. toctree::
   :maxdepth: 1

   reference/generics
   reference/protocols
   reference/best_practices
   reference/quality
   typing Module Documentation <https://docs.python.org/3/library/typing.html>

.. seealso::

   The documentation at https://mypy.readthedocs.io/ is relatively accessible
   and complete.

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

* `mypy <http://mypy-lang.org/>`_
* `pyrefly <https://pyrefly.org/>`_
* `pyright <https://github.com/microsoft/pyright>`_
* `ty <https://docs.astral.sh/ty/>`_
* `Zuban <https://docs.zubanls.com/en/latest/>`_

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
