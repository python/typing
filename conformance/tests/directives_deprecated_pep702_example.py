"""
Tests the warnings.deprecated function.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/directives.html#deprecated
# See also https://peps.python.org/pep-0702/

# > Type checkers should produce a diagnostic whenever they encounter a usage of an object
# > marked as deprecated. [...] For deprecated classes and functions, this includes:

# > * `from` imports

from _directives_deprecated_pep702_example import Ham  # E: Use of deprecated class Ham

import _directives_deprecated_pep702_example as library


# > * References through module, class, or instance attributes

library.norwegian_blue(1)  # E: Use of deprecated function norwegian_blue
map(library.norwegian_blue, [1, 2, 3])  # E: Use of deprecated function norwegian_blue


# > For deprecated overloads, this includes all calls that resolve to the deprecated overload.

library.foo(1)  # E: Use of deprecated overload for foo
library.foo("x")  # no error


ham = Ham()  # no error (already reported above)


# > Any syntax that indirectly triggers a call to the function.

spam = library.Spam()

spam.greasy  # E: Use of deprecated property Spam.greasy
spam.shape  # no error

spam.shape = "cube"  # E: Use of deprecated property setter Spam.shape
spam.shape += "cube"  # E: Use of deprecated property setter Spam.shape

spam + 1  # E: Use of deprecated method Spam.__add__
spam += 1  # E: Use of deprecated method Spam.__add__
