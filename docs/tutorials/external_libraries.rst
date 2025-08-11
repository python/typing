.. _external_libraries:

************************
Using External Libraries
************************

.. seealso::
    If you are looking for information on how to write type hints for
    external libraries, see the :ref:`writing_stubs` guide.

Many external libraries -- whether installed from the
`Python Package Index <https://pypi.org/>`_ (PyPI) or from other sources --
provide their own type hints. This is indicated by the presence of a
``py.typed`` file in the library's root directory. If you install such a
library, you can use it with any type checker without any additional
configuration.

Type hints can either be included in the library's source code the same way
as in your own code, or they can be provided in separate so-called
*stub files*. Stub files are named ``<module>.pyi`` and contain only type
hints, without any implementation.

For libraries that don't include their own type hints, a separate
*stub package* may provide them. These stub packages are often written by the
library authors themselves, by the contributors to the
`typeshed <https://github.com/python/typeshed>`_ project, or by third-party
contributors. These packages are usually named ``types-<library>``
or ``<library>-stubs``. These packages can be installed from PyPI as usual, and
they will be automatically discovered by type checkers::

    pip install requests types-requests

.. warning::

    The usual security considerations apply when installing third-party
    packages. Only install packages from sources you trust. Stub packages
    have the same security implications as any other package.

..
   TODO: Once development dependencies are supported by pyproject.toml,
   and described in https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
   we should recommend installing type stubs as a development dependency.
