Special types in annotations
============================

``Any``
-------

A special kind of type is ``Any``.  Every type is consistent with
``Any``.  It can be considered a type that has all values and all methods.
Note that ``Any`` and builtin type ``object`` are completely different.

When the type of a value is ``object``, the type checker will reject
almost all operations on it, and assigning it to a variable (or using
it as a return value) of a more specialized type is a type error.  On
the other hand, when a value has type ``Any``, the type checker will
allow all operations on it, and a value of type ``Any`` can be assigned
to a variable (or used as a return value) of a more constrained type.

A function parameter without an annotation is assumed to be annotated with
``Any``. If a generic type is used without specifying type parameters,
they are assumed to be ``Any``::

  from collections.abc import Mapping

  def use_map(m: Mapping) -> None:  # Same as Mapping[Any, Any]
      ...

This rule also applies to ``tuple``, in annotation context it is equivalent
to ``tuple[Any, ...]``. As well, a bare
``Callable`` in an annotation is equivalent to ``Callable[..., Any]``::

  from collections.abc import Callable

  def check_args(args: tuple) -> bool:
      ...

  check_args(())           # OK
  check_args((42, 'abc'))  # Also OK
  check_args(3.14)         # Flagged as error by a type checker

  # A list of arbitrary callables is accepted by this function
  def apply_callbacks(cbs: list[Callable]) -> None:
      ...

``Any`` can also be used as a base class. This can be useful for
avoiding type checker errors with classes that can duck type anywhere or
are highly dynamic.

``None``
--------

When used in a type hint, the expression ``None`` is considered
equivalent to ``type(None)``.

``NoReturn``
------------

The ``typing`` module provides a special type ``NoReturn`` to annotate functions
that never return normally. For example, a function that unconditionally
raises an exception::

  from typing import NoReturn

  def stop() -> NoReturn:
      raise RuntimeError('no way')

The ``NoReturn`` annotation is used for functions such as ``sys.exit``.
Static type checkers will ensure that functions annotated as returning
``NoReturn`` truly never return, either implicitly or explicitly::

  import sys
  from typing import NoReturn

    def f(x: int) -> NoReturn:  # Error, f(0) implicitly returns None
        if x != 0:
            sys.exit(1)

The checkers will also recognize that the code after calls to such functions
is unreachable and will behave accordingly::

  # continue from first example
  def g(x: int) -> int:
      if x > 0:
          return x
      stop()
      return 'whatever works'  # Error might be not reported by some checkers
                               # that ignore errors in unreachable blocks

The ``NoReturn`` type is only valid as a return annotation of functions,
and considered an error if it appears in other positions::

  from typing import NoReturn

  # All of the following are errors
  def bad1(x: NoReturn) -> int:
      ...
  bad2: NoReturn = None
  def bad3() -> list[NoReturn]:
      ...

``Never``
---------

Since Python 3.11, the ``typing`` module has a primitive ``Never``. This
represents the bottom type, a type that has no members. Type checkers are
expected to treat this type as equivalent to ``NoReturn``, but it is explicitly
also allowed in argument positions.

Tuples
------

The type of a tuple can be expressed by listing the element
types: ``tuple[int, int, str]`` is a tuple containing an int,
another int, and a str.  The empty tuple can be typed as
``tuple[()]``.  Arbitrary-length homogeneous tuples can be
expressed using one type and ellipsis, for example ``tuple[int, ...]``.

Special cases for ``float`` and ``complex``
-------------------------------------------

Python's numeric types ``complex``, ``float`` and ``int`` are not
subtypes of each other, but to support common use cases, the type
system contains a straightforward shortcut:
when an argument is annotated as having
type ``float``, an argument of type ``int`` is acceptable; similar,
for an argument annotated as having type ``complex``, arguments of
type ``float`` or ``int`` are acceptable.

``type[]``
----------

Sometimes you want to talk about class objects, in particular class
objects that inherit from a given class.  This can be spelled as
``type[C]`` where ``C`` is a class.  To clarify: while ``C`` (when
used as an annotation) refers to instances of class ``C``, ``type[C]``
refers to *subclasses* of ``C``.  (This is a similar distinction as
between ``object`` and ``type``.)

For example, suppose we have the following classes::

  class User: ...  # Abstract base for User classes
  class BasicUser(User): ...
  class ProUser(User): ...
  class TeamUser(User): ...

And suppose we have a function that creates an instance of one of
these classes if you pass it a class object::

  def new_user(user_class):
      user = user_class()
      # (Here we could write the user object to a database)
      return user

Without subscripting ``type[]`` the best we could do to annotate ``new_user()``
would be::

  def new_user(user_class: type) -> User:
      ...

However using ``type[]`` and a type variable with an upper bound we
can do much better::

  U = TypeVar('U', bound=User)
  def new_user(user_class: type[U]) -> U:
      ...

Now when we call ``new_user()`` with a specific subclass of ``User`` a
type checker will infer the correct type of the result::

  joe = new_user(BasicUser)  # Inferred type is BasicUser

The value corresponding to ``type[C]`` must be an actual class object
that's a subtype of ``C``, not a special form.  In other words, in the
above example calling e.g. ``new_user(BasicUser | ProUser)`` is
rejected by the type checker (in addition to failing at runtime
because you can't instantiate a union).

Note that it is legal to use a union of classes as the parameter for
``type[]``, as in::

  def new_non_team_user(user_class: type[BasicUser | ProUser]):
      user = new_user(user_class)
      ...

However the actual argument passed in at runtime must still be a
concrete class object, e.g. in the above example::

  new_non_team_user(ProUser)  # OK
  new_non_team_user(TeamUser)  # Disallowed by type checker

``type[Any]`` is also supported (see below for its meaning).

``type[T]`` where ``T`` is a type variable is allowed when annotating the
first argument of a class method (see the relevant section).

Any other special constructs like ``tuple`` or ``Callable`` are not allowed
as an argument to ``type``.

There are some concerns with this feature: for example when
``new_user()`` calls ``user_class()`` this implies that all subclasses
of ``User`` must support this in their constructor signature.  However
this is not unique to ``type[]``: class methods have similar concerns.
A type checker ought to flag violations of such assumptions, but by
default constructor calls that match the constructor signature in the
indicated base class (``User`` in the example above) should be
allowed.  A program containing a complex or extensible class hierarchy
might also handle this by using a factory class method.

When ``type`` is parameterized it requires exactly one parameter.
Plain ``type`` without brackets, the root of Python's metaclass
hierarchy, is equivalent to ``type[Any]``.

Regarding the behavior of ``type[Any]`` (or ``type``),
accessing attributes of a variable with this type only provides
attributes and methods defined by ``type`` (for example,
``__repr__()`` and ``__mro__``).  Such a variable can be called with
arbitrary arguments, and the return type is ``Any``.

``type`` is covariant in its parameter, because ``type[Derived]`` is a
subtype of ``type[Base]``::

  def new_pro_user(pro_user_class: type[ProUser]):
      user = new_user(pro_user_class)  # OK
      ...
