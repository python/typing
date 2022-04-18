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

`typing_extensions` supports Python versions 3.7 and up.

# Versioning scheme

Starting with version 4.0.0, `typing_extensions` uses
[Semantic Versioning](https://semver.org/). The major version is incremented for all
backwards-incompatible changes.

# Workflow for PyPI releases

- Ensure that GitHub Actions reports no errors.

- Update the version number in `typing_extensions/pyproject.toml` and in
  `typing_extensions/CHANGELOG.md`.

- Make sure your environment is up to date

 - `git checkout master`
 - `git pull`
 - `python -m pip install --upgrade build twine`

- Build the source and wheel distributions:

  - `cd typing_extensions`
  - `rm -rf dist/`
  - `python -m build .`

- Install the built distributions locally and test (if you were using `tox`, you already
  tested the source distribution).

- Run `twine upload dist/*`.

- Tag the release. The tag should be just the version number, e.g. `4.1.1`.

- `git push --tags`
