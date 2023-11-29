Type system concepts
====================

Union types
-----------

Since accepting a small, limited set of expected types for a single
argument is common, the type system supports union types, created with the
``|`` operator.
Example::

  def handle_employees(e: Employee | Sequence[Employee]) -> None:
      if isinstance(e, Employee):
          e = [e]
      ...

A type factored by ``T1 | T2 | ...`` is a supertype
of all types ``T1``, ``T2``, etc., so that a value that
is a member of one of these types is acceptable for an argument
annotated by ``T1 | T2 | ...``.

One common case of union types are *optional* types.  By default,
``None`` is an invalid value for any type, unless a default value of
``None`` has been provided in the function definition.  Examples::

  def handle_employee(e: Employee | None) -> None: ...

A past version of this specification allowed type checkers to assume an optional
type when the default value is ``None``, as in this code::

  def handle_employee(e: Employee = None): ...

This would have been treated as equivalent to::

  def handle_employee(e: Employee | None = None) -> None: ...

This is no longer the recommended behavior. Type checkers should move
towards requiring the optional type to be made explicit.

Support for singleton types in unions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A singleton instance is frequently used to mark some special condition,
in particular in situations where ``None`` is also a valid value
for a variable. Example::

  _empty = object()

  def func(x=_empty):
      if x is _empty:  # default argument value
          return 0
      elif x is None:  # argument was provided and it's None
          return 1
      else:
          return x * 2

To allow precise typing in such situations, the user should use
a union type in conjunction with the ``enum.Enum`` class provided
by the standard library, so that type errors can be caught statically::

  from enum import Enum

  class Empty(Enum):
      token = 0
  _empty = Empty.token

  def func(x: int | None | Empty = _empty) -> int:

      boom = x * 42  # This fails type check

      if x is _empty:
          return 0
      elif x is None:
          return 1
      else:  # At this point typechecker knows that x can only have type int
          return x * 2

Since the subclasses of ``Enum`` cannot be further subclassed,
the type of variable ``x`` can be statically inferred in all branches
of the above example. The same approach is applicable if more than one
singleton object is needed: one can use an enumeration that has more than
one value::

  class Reason(Enum):
      timeout = 1
      error = 2

  def process(response: str | Reason = '') -> str:
      if response is Reason.timeout:
          return 'TIMEOUT'
      elif response is Reason.error:
          return 'ERROR'
      else:
          # response can be only str, all other possible values exhausted
          return 'PROCESSED: ' + response
