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

  if sys.version_info >= (3, 12):
      # Python 3.12+
  else:
      # Python 3.11 and lower

  if sys.platform == 'win32':
      # Windows specific definitions
  else:
      # Posix specific definitions

Don't expect a checker to understand obfuscations like
``"".join(reversed(sys.platform)) == "xunil"``.

``@deprecated``
---------------

(Originally specified in :pep:`702`.)

The :py:func:`warnings.deprecated`
decorator can be used on a class, function or method to mark it as deprecated.
This includes :class:`typing.TypedDict` and :class:`typing.NamedTuple` definitions.
With overloaded functions, the decorator may be applied to individual overloads,
indicating that the particular overload is deprecated. The decorator may also be
applied to the overload implementation function, indicating that the entire function
is deprecated.

The decorator takes the following arguments:

* A required positional-only argument representing the deprecation message.
* Two keyword-only arguments, ``category`` and ``stacklevel``, controlling
  runtime behavior (see under "Runtime behavior" below).

The positional-only argument is of type ``str`` and contains a message that should
be shown by the type checker when it encounters a usage of the decorated object.
Tools may clean up the deprecation message for display, for example
by using :func:`inspect.cleandoc` or equivalent logic.
The message must be a string literal.
The content of deprecation messages is up to the user, but it may include the version
in which the deprecated object is to be removed, and information about suggested
replacement APIs.

Type checkers should produce a diagnostic whenever they encounter a usage of an
object marked as deprecated. For deprecated overloads, this includes all calls
that resolve to the deprecated overload.
For deprecated classes and functions, this includes:

* References through module, class, or instance attributes (``module.deprecated_object``,
  ``module.SomeClass.deprecated_method``, ``module.SomeClass().deprecated_method``)
* Any usage of deprecated objects in their defining module
  (``x = deprecated_object()`` in ``module.py``)
* If ``import *`` is used, usage of deprecated objects from the
  module (``from module import *; x = deprecated_object()``)
* ``from`` imports (``from module import deprecated_object``)
* Any syntax that indirectly triggers a call to the function. For example,
  if the ``__add__`` method of a class ``C`` is deprecated, then
  the code ``C() + C()`` should trigger a diagnostic. Similarly, if the
  setter of a property is marked deprecated, attempts to set the property
  should trigger a diagnostic.

If a method is marked with the :func:`typing.override` decorator from :pep:`698`
and the base class method it overrides is deprecated, the type checker should
produce a diagnostic.

There are additional scenarios where deprecations could come into play.
For example, an object may implement a :class:`typing.Protocol`, but one
of the methods required for protocol compliance is deprecated.
As scenarios such as this one appear complex and relatively unlikely to come up in practice,
this PEP does not mandate that type checkers detect them.

Example
^^^^^^^

As an example, consider this library stub named ``library.pyi``:

.. code-block:: python

   from warnings import deprecated

   @deprecated("Use Spam instead")
   class Ham: ...

   @deprecated("It is pining for the fiords")
   def norwegian_blue(x: int) -> int: ...

   @overload
   @deprecated("Only str will be allowed")
   def foo(x: int) -> str: ...
   @overload
   def foo(x: str) -> str: ...

   class Spam:
       @deprecated("There is enough spam in the world")
       def __add__(self, other: object) -> object: ...

       @property
       @deprecated("All spam will be equally greasy")
       def greasy(self) -> float: ...

       @property
       def shape(self) -> str: ...
       @shape.setter
       @deprecated("Shapes are becoming immutable")
       def shape(self, value: str) -> None: ...

Here is how type checkers should handle usage of this library:

.. code-block:: python

   from library import Ham  # error: Use of deprecated class Ham. Use Spam instead.

   import library

   library.norwegian_blue(1)  # error: Use of deprecated function norwegian_blue. It is pining for the fiords.
   map(library.norwegian_blue, [1, 2, 3])  # error: Use of deprecated function norwegian_blue. It is pining for the fiords.

   library.foo(1)  # error: Use of deprecated overload for foo. Only str will be allowed.
   library.foo("x")  # no error

   ham = Ham()  # no error (already reported above)

   spam = library.Spam()
   spam + 1  # error: Use of deprecated method Spam.__add__. There is enough spam in the world.
   spam.greasy  # error: Use of deprecated property Spam.greasy. All spam will be equally greasy.
   spam.shape  # no error
   spam.shape = "cube"  # error: Use of deprecated property setter Spam.shape. Shapes are becoming immutable.

The exact wording of the diagnostics is up to the type checker and is not part
of the specification.

Type checker behavior
^^^^^^^^^^^^^^^^^^^^^

It is unspecified exactly how type checkers should present deprecation
diagnostics to their users. However, some users (e.g., application developers
targeting only a specific version of Python) may not care about deprecations,
while others (e.g., library developers who want their library to remain
compatible with future versions of Python) would want to catch any use of
deprecated functionality in their CI pipeline. Therefore, it is recommended
that type checkers provide configuration options that cover both use cases.
As with any other type checker error, it is also possible to ignore deprecations
using ``# type: ignore`` comments.
