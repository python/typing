"""
Tests the "alternative" (non-class) syntax for defining a TypedDict.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/typeddict.html#alternative-syntax

from typing import TypedDict


Movie = TypedDict("Movie", {"name": str, "year": int, "illegal key name": bool})

movie: Movie = {"name": "Blade Runner", "year": 1982, "illegal key name": True}

MovieOptional = TypedDict("MovieOptional", {"name": str, "year": int}, total=False)

movie_opt1: MovieOptional = {}
movie_opt2: MovieOptional = {"year": 1982}

# > A type checker is only expected to accept a dictionary display expression as
# > the second argument to TypedDict. In particular, a variable that refers to a
# > dictionary object does not need to be supported, to simplify implementation.
my_dict = {"name": str}
BadTypedDict1 = TypedDict("BadTypedDict1", my_dict)


# This should generate an error because it uses a non-str key.
BadTypedDict2 = TypedDict("BadTypedDict2", {1: str})


# This should generate an error because it uses a non-matching name.
BadTypedDict3 = TypedDict("WrongName", {"name": str})


# This should generate an error because of the additional parameter.
BadTypedDict4 = TypedDict("BadTypedDict4", {"name": str}, total=False, other=False)


# > The keyword-argument syntax is deprecated in 3.11 and will be removed in 3.13.
# > It may also be unsupported by static type checkers.

Movie2 = TypedDict("Movie2", name=str, year=int)

movie2: Movie2
movie2 = {"name": "Blade Runner", "year": 1982}
movie2 = {"name": "Blade Runner", "year": ""}  # Type error: Incorrect type for year
