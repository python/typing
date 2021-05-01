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
