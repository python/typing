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


def func1(variable_key: str, existing_movie: Movie):
    # > A key that is not a literal should generally be rejected.
    movie: Movie = {variable_key: "", "year": 1900}  # E: variable key

    # Destructive operations.
    existing_movie[variable_key] = 1982  # E: variable key
    del existing_movie[variable_key]  # E

    # Read-only operations.
    reveal_type(existing_movie[variable_key])  # E

    # Exceptions.
    reveal_type(variable_key in existing_movie)  # `bool`
    assert_type(existing_movie.get(variable_key), object | None)


# It's not clear from the spec what type this should be.
movie.get("name")

# It's not clear from the spec what type this should be.
movie.get("other")  # E?

# It's not clear from the spec whether it's allowed.
reveal_type("other" in movie)  # E?

movie.clear()  # E: clear not allowed
movie.popitem()  # E: popitem not allowed

del movie["name"]  # E: del not allowed for required key



class MovieOptional(TypedDict, total=False):
    name: str
    year: int


movie_optional: MovieOptional = {}

# > Type checkers may allow reading an item using d['x']
# even if the key 'x' is not required.
movie_optional["name"]  # E?
assert_type(movie_optional.get("name"), str | None)

# It's not clear from the spec what type this should be.
reveal_type(movie_optional.get("other"))  # E?

# It's not clear from the spec whether it's allowed.
reveal_type("other" in movie_optional)  # E?

movie_optional.clear()  # E: clear not allowed
movie_optional.popitem()  # E: popitem not allowed

del movie_optional["name"]


def func2(variable_key: str, existing_optional_movie: MovieOptional):
    # > A key that is not a literal should generally be rejected.
    movie_optional: MovieOptional = {variable_key: "", "year": 1900}  # E: variable key

    # Destructive operations.
    existing_optional_movie[variable_key] = 1982  # E: variable key
    del existing_optional_movie[variable_key]  # E: variable key

    # Read-only operations.
    reveal_type(existing_optional_movie[variable_key])  # E

    # Exceptions.
    reveal_type(variable_key in existing_optional_movie)  # `bool`
    assert_type(existing_optional_movie.get(variable_key), object | None)
