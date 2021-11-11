Python Typing Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reading the docs
=================

The live documentation for Python's static typing can be found at
`typing.readthedocs.io <https://typing.readthedocs.io/>`_.

Building the docs
=================

The documentation is built with tools which are not included in this
tree but are maintained separately and are available from
`PyPI <https://pypi.org/>`_.

* `Sphinx <https://pypi.org/project/Sphinx/>`_
* `python-docs-theme <https://pypi.org/project/python-docs-theme/>`_

The easiest way to install these tools is to create a virtual environment and
install the tools into there.

Using make
----------

To get started on UNIX, you can create a virtual environment with the command ::

  make venv

That will install all the tools necessary to build the documentation. Assuming
the virtual environment was created in the ``venv`` directory (the default;
configurable with the VENVDIR variable), you can run the following command to
build the HTML output files::

  make html

By default, if the virtual environment is not created, the Makefile will
look for instances of sphinxbuild and blurb installed on your process PATH
(configurable with the SPHINXBUILD and BLURB variables).

Available make targets are:

* "clean", which removes all build files.

* "venv", which creates a virtual environment with all necessary tools
  installed.

* "html", which builds standalone HTML files for offline viewing.

* "text", which builds a plain text file for each source file.
