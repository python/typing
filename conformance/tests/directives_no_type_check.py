"""
Tests the typing.no_type_check decorator.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/directives.html#no-type-check

from typing import no_type_check

# > To mark portions of the program that should not be covered by type hinting,
# > you can use the @typing.no_type_check decorator on a class or function.
# > Functions with this decorator should be treated as having no annotations.


@no_type_check
class ClassA:
    x: int = ""  # No error should be reported


@no_type_check
def func1(a: int, b: str) -> None:
    c = a + b  # No error should be reported
    return 1  # No error should be reported


func1(b"invalid", b"arguments")  # No error should be reported
func1()  # E: incorrect arguments for parameters
