Code in this repository should follow CPython's style guidelines and
contributors need to sign the PSF Contributor Agreement.

# typing\_extensions

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

`typing_extensions` supports Python versions 3.6 an up.

# Versioning scheme

Starting with version 4.0.0, `typing_extensions` uses
[Semantic Versioning](https://semver.org/). The major version is incremented for all
backwards-incompatible changes.

# Workflow for PyPI releases

- Ensure that GitHub Actions reports no errors.

- Update the version number in `setup.py`.

- Build the source and wheel distributions:

  - `pip3 install -U setuptools wheel`
  - `pip2 install -U setuptools wheel`
  - `rm -rf dist/ build/`
  - `python3 setup.py sdist bdist_wheel`
  - `rm -rf build/` (Works around
    `a Wheel bug <https://bitbucket.org/pypa/wheel/issues/147/bdist_wheel-should-start-by-cleaning-up>`\_)
  - `python2 setup.py bdist_wheel`

- Install the built distributions locally and test (if you were using `tox`, you already
  tested the source distribution).

- Make sure twine is up to date, then run `twine upload dist/*`.
