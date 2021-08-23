.. typing documentation master file, created by
   sphinx-quickstart on Mon May 24 16:43:52 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the Python Type System documentation!
================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   stubs


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

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

* `PyCharm <https://www.jetbrains.com/de-de/pycharm/>`_, an IDE that supports
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
