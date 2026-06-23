"""
Tests operations provided by a TypedDict object.
"""

# Specification: https://typing.readthedocs.io/en/latest/spec/typeddict.html#supported-and-unsupported-operations


from typing import TypedDict, assert_type


class Movie(TypedDict):
    name: str
    year: int


movie: Movie

movie = {"name": "Blade Runner", "year": 1982}
movie["name"] = "Other"
movie["year"] = 1981

movie["name"] = 1982  # E: wrong type
movie["year"] = ""  # E: wrong type
movie["other"] = ""  # E: unknown key added

print(movie["other"]) # E: unknown key referenced

movie = {"name": "Blade Runner"}  # E: year is missing
movie = {"name": "Blade Runner", "year": 1982.1}  # E: year is wrong type

# > The use of a key that is not known to exist should be reported as an error.
movie = {"name": "", "year": 1900, "other": 2}  # E: extra key


def func1(variable_key: str):
    # > A key that is not a literal should generally be rejected.
    movie: Movie = {variable_key: "", "year": 1900}  # E: variable key


# > For required keys, type checkers may return either the declared type T
# > or T | None.
movie.get("name")

# > If ``e`` is a string literal that is not a defined key of ``d``,
# > no error should be reported.
movie.get("other")


movie.clear()  # E: clear not allowed

del movie["name"]  # E: del not allowed for required key



class MovieOptional(TypedDict, total=False):
    name: str
    year: int


movie_optional: MovieOptional = {}

assert_type(movie_optional.get("name"), str | None)

movie_optional.clear()  # E: clear not allowed

del movie_optional["name"]
