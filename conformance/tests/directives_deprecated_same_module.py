"""
Tests the warnings.deprecated function when a deprecated symbol is used in the same module.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/directives.html#deprecated
# See also https://peps.python.org/pep-0702/

# > Type checkers should produce a diagnostic whenever they encounter a usage of an object
# > marked as deprecated. [...] For deprecated classes and functions, this includes:
# >
# > * Any usage of deprecated objects in their defining module

from typing_extensions import deprecated


@deprecated("Deprecated")
def lorem() -> None: ...


ipsum = lorem()  # E: Use of deprecated function lorem
