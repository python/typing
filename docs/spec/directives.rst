.. _directives:

Type checker directives
=======================

``assert_type()``
-----------------

The function ``typing.assert_type(val, typ)`` allows users to
ask a static type checker to confirm that *val* has an inferred type of *typ*.

When a type checker encounters a call to ``assert_type()``, it
should emit an error if the value is not of the specified type::

    def greet(name: str) -> None:
        assert_type(name, str)  # OK, inferred type of `name` is `str`
        assert_type(name, int)  # type checker error

``reveal_type()``
-----------------

The function ``reveal_type(obj)`` makes type checkers
reveal the inferred static type of an expression.

When a static type checker encounters a call to this function,
it should emit a diagnostic with the type of the argument. For example::

  x: int = 1
  reveal_type(x)  # Revealed type is "builtins.int"

``# type: ignore`` comments
---------------------------

The special comment ``# type: ignore`` is used to silence type checker
errors.

The ``# type: ignore`` comment should be put on the line that the
error refers to::

  import http.client
  errors = {
      'not_found': http.client.NOT_FOUND  # type: ignore
  }

A ``# type: ignore`` comment on a line by itself at the top of a file,
before any docstrings, imports, or other executable code, silences all
errors in the file. Blank lines and other comments, such as shebang
lines and coding cookies, may precede the ``# type: ignore`` comment.

In some cases, linting tools or other comments may be needed on the same
line as a type comment. In these cases, the type comment should be before
other comments and linting markers:

  # type: ignore # <comment or other marker>

``cast()``
----------

Occasionally the type checker may need a different kind of hint: the
programmer may know that an expression is of a more constrained type
than a type checker may be able to infer.  For example::

  from typing import cast

  def find_first_str(a: list[object]) -> str:
      index = next(i for i, x in enumerate(a) if isinstance(x, str))
      # We only get here if there's at least one string in a
      return cast(str, a[index])

Some type checkers may not be able to infer that the type of
``a[index]`` is ``str`` and only infer ``object`` or ``Any``, but we
know that (if the code gets to that point) it must be a string.  The
``cast(t, x)`` call tells the type checker that we are confident that
the type of ``x`` is ``t``.  At runtime a cast always returns the
expression unchanged -- it does not check the type, and it does not
convert or coerce the value.

Casts differ from type comments (see the previous section).  When using
a type comment, the type checker should still verify that the inferred
type is consistent with the stated type.  When using a cast, the type
checker should blindly believe the programmer.  Also, casts can be used
in expressions, while type comments only apply to assignments.

``TYPE_CHECKING``
-----------------

Sometimes there's code that must be seen by a type checker (or other
static analysis tools) but should not be executed.  For such
situations the ``typing`` module defines a constant,
``TYPE_CHECKING``, that is considered ``True`` during type checking
(or other static analysis) but ``False`` at runtime.  Example::

  import typing

  if typing.TYPE_CHECKING:
      import expensive_mod

  def a_func(arg: 'expensive_mod.SomeClass') -> None:
      a_var: expensive_mod.SomeClass = arg
      ...

(Note that the type annotation must be enclosed in quotes, making it a
"forward reference", to hide the ``expensive_mod`` reference from the
interpreter runtime.  In the variable annotation no quotes are needed.)

This approach may also be useful to handle import cycles.

``@no_type_check``
------------------

To mark portions of the program that should not be covered by type
hinting, you can use the ``@typing.no_type_check`` decorator on a class or function.
Functions with this decorator should be treated as having
no annotations.

Version and platform checking
-----------------------------

Type checkers are expected to understand simple version and platform
checks, e.g.::

  import sys

  if sys.version_info[0] >= 3:
      # Python 3 specific definitions
  else:
      # Python 2 specific definitions

  if sys.platform == 'win32':
      # Windows specific definitions
  else:
      # Posix specific definitions

Don't expect a checker to understand obfuscations like
``"".join(reversed(sys.platform)) == "xunil"``.
