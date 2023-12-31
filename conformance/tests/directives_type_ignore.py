"""
Tests "# type: ignore" comments.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/directives.html#type-ignore-comments

# The following type violation should be suppressed.
x: int = ""  # type: ignore

# The following type violation should be suppressed.
y: int = ""  # type: ignore - additional stuff

# The following type violation should be suppressed.
z: int = ""  # type: ignore[additional_stuff]
