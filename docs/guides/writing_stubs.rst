.. _writing_stubs:

**********************************
Writing and Maintaining Stub Files
**********************************

Stub files are a means of providing type information for Python modules.
For a full reference, refer to :ref:`stubs`.

Maintaining stubs can be a little cumbersome because they are separated from the
implementation. This page lists some tools that make writing and maintaining
stubs less painful.

Tools for generating stubs
==========================

stubgen
-------

stubgen is a tool bundled with `mypy <https://github.com/python/mypy>`__
that can be used to generate basic stubs. These stubs serve as a
basic starting point; most types will default to ``Any``.

.. code-block:: console

    stubgen -p my_great_package

For more details, see `stubgen docs <https://mypy.readthedocs.io/en/stable/stubgen.html>`__.

pyright
-------

pyright contains a tool that generates basic stubs. Like stubgen, these generated
stubs serve more as a starting point.

.. code-block:: console

    pyright --createstub my_great_package

For more details, see `pyright docs <https://github.com/microsoft/pyright/blob/main/docs/type-stubs.md#generating-type-stubs-from-command-line>`__.

monkeytype
----------

monkeytype takes a slightly different approach — you run your code (perhaps via
your tests) and monkeytype collects the types it observes at runtime to generate
stubs.

.. code-block:: console

    monkeytype run script.py
    monkeytype stub my_great_package

For more details, see `monkeytype docs <https://monkeytype.readthedocs.io/en/latest/>`__.

Tools for maintaining stubs
===========================

stubtest
--------

stubtest is a tool bundled with `mypy <https://github.com/python/mypy>`__.

stubtest finds inconsistencies between stub files and the implementation. It
does this by comparing stub definitions to what it finds from importing your
code and using runtime introspection (via the ``inspect`` module).

.. code-block:: console

    stubtest my_great_package

For more details, see `stubtest docs <https://mypy.readthedocs.io/en/stable/stubtest.html>`__.

flake8-pyi
----------

flake8-pyi is a `flake8 <https://flake8.pycqa.org/en/latest/>`__ plugin that
lints common issues in stub files.

.. code-block:: console

    flake8 my_great_package

For more details, see `flake8-pyi docs <https://github.com/PyCQA/flake8-pyi>`__.

Running a type checker on the stubs
-----------------------------------

Simply running a type checker on the stubs can catch several issues, from simple
things like detecting missing annotations to more complex things like ensuring
Liskov substitutability or detecting problematic overloads.

It may be instructive to examine `typeshed <https://github.com/python/typeshed/>`__'s
`setup for testing stubs <https://github.com/python/typeshed/blob/main/tests/README.md>`__.

..
   TODO: consider adding examples and configurations for specific type checkers

Type checking usage of your package
-----------------------------------

If you have access to a codebase that uses your package — perhaps tests for your
package — running a type checker against it can help you detect issues,
particularly with false positives.

If your package has some particularly complex aspects, you could even consider
writing dedicated typing tests for tricky definitions. For more details, see
:ref:`testing`.
