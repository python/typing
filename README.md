[![Chat at https://gitter.im/python/typing](https://badges.gitter.im/python/typing.svg)](https://gitter.im/python/typing?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

PEP 484: Type Hints
===================

This GitHub repo is used for three separate things:

- The issue tracker is used to discuss PEP-level type system issues.
  However,
  [typing-sig](https://mail.python.org/mailman3/lists/typing-sig.python.org/)
  is more appropriate these days.

- A copy of the `typing` module for older Python versions (2.7 and
  3.4) is maintained here.  Note that the canonical source lives
  [upstream](https://github.com/python/cpython/blob/master/Lib/typing.py)
  in the CPython repo.

- The `typing_extensions` module lives here.

Workflow
--------

* The typing.py module and its unittests are edited in the `src`
  subdirectory of this repo. The `python2` subdirectory contains the
  Python 2 backport.

Workflow for PyPI releases
--------------------------

* Run tests under all supported versions. As of April 2021 this includes
  2.7, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9.

* On macOS, you can use `pyenv <https://github.com/pyenv/pyenv>`_ to
  manage multiple Python installations. Long story short:

  * ``xcode-select --install``
  * ``brew install pyenv``
  * ``echo 'eval "$(pyenv init -)"' >> ~/.bash_profile``
  * Open a new shell
  * ``pyenv install 3.5.3``
  * ``pyenv install 3.4.6``
  * (assuming you already have 2.7.13 and 3.6.1 from Homebrew)
  * ``pyenv global system 3.5.3 3.4.6``

* You can use ``tox`` to automate running tests.

* Update the version number in ``setup.py``.

* Build the source and wheel distributions:

  * ``pip3 install -U setuptools wheel``
  * ``pip2 install -U setuptools wheel``
  * ``rm -rf dist/ build/``
  * ``python3 setup.py sdist bdist_wheel``
  * ``rm -rf build/`` (Works around `a Wheel bug <https://bitbucket.org/pypa/wheel/issues/147/bdist_wheel-should-start-by-cleaning-up>`_)
  * ``python2 setup.py bdist_wheel``

* Install the built distributions locally and test (if you
  were using ``tox``, you already tested the source distribution).

* Make sure twine is up to date, then run ``twine upload dist/*``.
