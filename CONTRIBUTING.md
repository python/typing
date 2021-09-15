Code in this repository should follow CPython's style guidelines and
contributors need to sign the PSF Contributor Agreement.

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

`typing_extensions` supports Python 3.6+. However, it is OK to omit support for Python versions that have
reached end of life if doing so is too difficult or otherwise does not make sense. For
example, `typing_extensions.AsyncGenerator` only exists on Python 3.6 and higher,
because async generators were added to the language in 3.6.

# Versioning scheme

The version number of `typing_extensions` indicates the version of the standard library `typing`
module that is reflected in the backport. For example, `typing_extensions` version
3.10.0.0 includes features from the Python 3.10.0 standard library's `typing` module. A
new release that doesn't include any new standard library features would be called
3.10.0.1.

# Workflow for PyPI releases

- Ensure that GitHub Actions reports no errors.

- Update the version number in `setup.py`.

- Build the source and wheel distributions:

  - `pip3 install -U setuptools wheel`
  - `rm -rf dist/ build/`
  - `python3 setup.py sdist bdist_wheel`

- Install the built distributions locally and test (if you were using `tox`, you already
  tested the source distribution).

- Make sure twine is up to date, then run `twine upload dist/*`.
