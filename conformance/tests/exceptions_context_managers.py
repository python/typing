"""
Tests the handling of __exit__ return types for context managers.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/exceptions.html


from typing import Any, Literal


class CMBase:
    def __enter__(self) -> None:
        pass


class Suppress1(CMBase):
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        return True


class Suppress2(CMBase):
    def __exit__(self, exc_type, exc_value, traceback) -> Literal[True]:
        return True


class NoSuppress1(CMBase):
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None


class NoSuppress2(CMBase):
    def __exit__(self, exc_type, exc_value, traceback) -> Literal[False]:
        return False


class NoSuppress3(CMBase):
    def __exit__(self, exc_type, exc_value, traceback) -> Any:
        return False


class NoSuppress4(CMBase):
    def __exit__(self, exc_type, exc_value, traceback) -> None | bool:
        return None


def func1() -> None:
    with Suppress1():
        raise ValueError("This exception is suppressed")

    return 1  # E


def func2() -> None:
    with Suppress2():
        raise ValueError("This exception is suppressed")

    return 1  # E


def func3() -> None:
    with NoSuppress1():
        raise ValueError("This exception is not suppressed")

    return 1  # OK


def func4() -> None:
    with NoSuppress2():
        raise ValueError("This exception is not suppressed")

    return 1  # OK


def func5() -> None:
    with NoSuppress3():
        raise ValueError("This exception is not suppressed")

    return 1  # OK


def func6() -> None:
    with NoSuppress4():
        raise ValueError("This exception is not suppressed")

    return 1  # OK
