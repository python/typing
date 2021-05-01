This repository contains backports of the CPython `typing` module to earlier versions of
Python. As such, follow CPython's contribution guidelines as much as possible when
contributing code here.

# typing

The `typing` module provided by this repository is a backport for Python versions that
do not have `typing` in the standard library: Python 2.7 and 3.4. These versions are no
longer officially supported by CPython, so there is little remaining interest in keeping
the backport up to date. We will accept contributions backporting new features to
`typing`, but we are no longer actively requiring Python 2 support for all
contributions.

# typing_extensions

The `typing_extensions` module provides a way to access new features from the standard
library `typing` module in older versions of Python. For example, Python 3.10 adds
`typing.TypeGuard`, but users of older versions of Python can use `typing_extensions` to
use `TypeGuard` in their code even if they are unable to upgrade to Python 3.10.

If you contribute the runtime implementation of a new `typing` feature to CPython, you
are encouraged to also implement the feature in `typing_extensions`. Because the runtime
implementation of much of the infrastructure in the `typing` module has changed over
time, this may require different code for some older Python versions.

`typing_extensions` may also include experimental features that are not yet part of the
standard library, so that users can experiment with them before they are added to the
standard library. Such features should ideally already be specified in a PEP or draft
PEP.

# Versioning scheme

`typing_extensions` and `typing` are usually released together using the same version
numbers. The version number indicates the version of the standard library `typing`
module that is reflected in the backport. For example, `typing_extensions` version
3.10.0.0 includes features from the Python 3.10.0 standard library's `typing` module. A
new release that doesn't include any new standard library features would be called
3.10.0.1.


# Workflow for PyPI releases

* Do this for both `typing` and `typing_extensions`

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
  * (or some more recent versions)

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
