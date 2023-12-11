.. _historical:

Historical and deprecated features
==================================

Over the course of the development of the Python type system, several
changes were made to the Python grammar and standard library to make it
easier to use the type system. This specification aims to use the more
modern syntax in all examples, but type checkers should generally support
the older alternatives and treat them as equivalent.

This section lists all of these cases.

Type comments
-------------

No first-class syntax support for explicitly marking variables as being
of a specific type existed when the type system was first designed.
To help with type inference in
complex cases, a comment of the following format may be used::

  x = []                # type: list[Employee]
  x, y, z = [], [], []  # type: list[int], list[int], list[str]
  x, y, z = [], [], []  # type: (list[int], list[int], list[str])
  a, b, *c = range(5)   # type: float, float, list[float]
  x = [1, 2]            # type: list[int]

Type comments should be put on the last line of the statement that
contains the variable definition.

These should be treated as equivalent to annotating the variables
using :pep:`526` variable annotations::

  x: list[Employee] = []
  x: list[int]
  y: list[int]
  z: list[str]
  x, y, z = [], [], []
  a: float
  b: float
  c: list[float]
  a, b, *c = range(5)
  x: list[int] = [1, 2]

Type comments can also be placed on
``with`` statements and ``for`` statements, right after the colon.

Examples of type comments on ``with`` and ``for`` statements::

  with frobnicate() as foo:  # type: int
      # Here foo is an int
      ...

  for x, y in points:  # type: float, float
      # Here x and y are floats
      ...

In stubs it may be useful to declare the existence of a variable
without giving it an initial value.  This can be done using :pep:`526`
variable annotation syntax::

  from typing import IO

  stream: IO[str]

The above syntax is acceptable in stubs for all versions of Python.
However, in non-stub code for versions of Python 3.5 and earlier
there is a special case::

  from typing import IO

  stream = None  # type: IO[str]

Type checkers should not complain about this (despite the value
``None`` not matching the given type), nor should they change the
inferred type to ``... | None``.  The
assumption here is that other code will ensure that the variable is
given a value of the proper type, and all uses can assume that the
variable has the given type.

Type comments on function definitions
-------------------------------------

Some tools may want to support type annotations in code that must be
compatible with Python 2.7.  For this purpose function annotations can be placed in
a ``# type:`` comment.  Such a comment must be placed immediately
following the function header (before the docstring).  An example: the
following Python 3 code::

  def embezzle(self, account: str, funds: int = 1000000, *fake_receipts: str) -> None:
      """Embezzle funds from account using fake receipts."""
      <code goes here>

is equivalent to the following::

  def embezzle(self, account, funds=1000000, *fake_receipts):
      # type: (str, int, *str) -> None
      """Embezzle funds from account using fake receipts."""
      <code goes here>

Note that for methods, no type is needed for ``self``.

For an argument-less method it would look like this::

  def load_cache(self):
      # type: () -> bool
      <code>

Sometimes you want to specify the return type for a function or method
without (yet) specifying the argument types.  To support this
explicitly, the argument list may be replaced with an ellipsis.
Example::

  def send_email(address, sender, cc, bcc, subject, body):
      # type: (...) -> bool
      """Send an email message.  Return True if successful."""
      <code>

Sometimes you have a long list of parameters and specifying their
types in a single ``# type:`` comment would be awkward.  To this end
you may list the arguments one per line and add a ``# type:`` comment
per line after an argument's associated comma, if any.
To specify the return type use the ellipsis syntax. Specifying the return
type is not mandatory and not every argument needs to be given a type.
A line with a ``# type:`` comment should contain exactly one argument.
The type comment for the last argument (if any) should precede the close
parenthesis. Example::

  def send_email(address,     # type: Union[str, List[str]]
                 sender,      # type: str
                 cc,          # type: Optional[List[str]]
                 bcc,         # type: Optional[List[str]]
                 subject='',
                 body=None    # type: List[str]
                 ):
      # type: (...) -> bool
      """Send an email message.  Return True if successful."""
      <code>

Notes:

- Tools that support this syntax should support it regardless of the
  Python version being checked.  This is necessary in order to support
  code that straddles Python 2 and Python 3.

- It is not allowed for an argument or return value to have both
  a type annotation and a type comment.

- When using the short form (e.g. ``# type: (str, int) -> None``)
  every argument must be accounted for, except the first argument of
  instance and class methods (those are usually omitted, but it's
  allowed to include them).

- The return type is mandatory for the short form.  If in Python 3 you
  would omit some argument or the return type, the Python 2 notation
  should use ``Any``.

- When using the short form, for ``*args`` and ``**kwds``, put 1 or 2
  stars in front of the corresponding type annotation.  (As with
  Python 3 annotations, the annotation here denotes the type of the
  individual argument values, not of the tuple/dict that you receive
  as the special argument value ``args`` or ``kwds``.)

- Like other type comments, any names used in the annotations must be
  imported or defined by the module containing the annotation.

- When using the short form, the entire annotation must be one line.

- The short form may also occur on the same line as the close
  parenthesis, e.g.::

    def add(a, b):  # type: (int, int) -> int
        return a + b

- Misplaced type comments will be flagged as errors by a type checker.
  If necessary, such comments could be commented twice. For example::

    def f():
        '''Docstring'''
        # type: () -> None  # Error!

    def g():
        '''Docstring'''
        # # type: () -> None  # This is OK

When checking Python 2.7 code, type checkers should treat the ``int`` and
``long`` types as equivalent. For parameters typed as ``Text``, arguments of
type ``str`` as well as ``unicode`` should be acceptable.


Positional-only arguments
-------------------------

Some functions are designed to take their arguments only positionally,
and expect their callers never to use the argument's name to provide
that argument by keyword. Before Python 3.8 (:pep:`570`), Python did
not provide a way to declare positional-only arguments.

To support positional-only arguments on older Python versions, type
checkers support the following special case:
all arguments with names beginning with
``__`` are assumed to be positional-only, except if their names also
end with ``__``::

  def quux(__x: int, __y__: int = 0) -> None: ...

  quux(3, __y__=1)  # This call is fine.

  quux(__x=3)  # This call is an error.


Generics in standard collections
--------------------------------

Before Python 3.9 (:pep:`585`), standard library generic types like
``list`` could not be parameterized at runtime (i.e., ``list[int]``
would throw an error). Therefore, the ``typing`` module provided
generic aliases for major builtin and standard library types (e.g.,
``typing.List[int]``).

In each of these cases, type checkers should treat the library type
as equivalent to the alias in the ``typing`` module. This includes:

* ``list`` and ``typing.List``
* ``dict`` and ``typing.Dict``
* ``set`` and ``typing.Set``
* ``frozenset`` and ``typing.FrozenSet``
* ``tuple`` and ``typing.Tuple``
* ``type`` and ``typing.Type``
* ``collections.deque`` and ``typing.Deque``
* ``collections.defaultdict`` and ``typing.DefaultDict``
* ``collections.OrderedDict`` and ``typing.OrderedDict``
* ``collections.Counter`` and ``typing.Counter``
* ``collections.ChainMap`` and ``typing.ChainMap``
* ``collections.abc.Awaitable`` and ``typing.Awaitable``
* ``collections.abc.Coroutine`` and ``typing.Coroutine``
* ``collections.abc.AsyncIterable`` and ``typing.AsyncIterable``
* ``collections.abc.AsyncIterator`` and ``typing.AsyncIterator``
* ``collections.abc.AsyncGenerator`` and ``typing.AsyncGenerator``
* ``collections.abc.Iterable`` and ``typing.Iterable``
* ``collections.abc.Iterator`` and ``typing.Iterator``
* ``collections.abc.Generator`` and ``typing.Generator``
* ``collections.abc.Reversible`` and ``typing.Reversible``
* ``collections.abc.Container`` and ``typing.Container``
* ``collections.abc.Collection`` and ``typing.Collection``
* ``collections.abc.Callable`` and ``typing.Callable``
* ``collections.abc.Set`` and ``typing.AbstractSet`` (note the change in name)
* ``collections.abc.MutableSet`` and ``typing.MutableSet``
* ``collections.abc.Mapping`` and ``typing.Mapping``
* ``collections.abc.MutableMapping`` and ``typing.MutableMapping``
* ``collections.abc.Sequence`` and ``typing.Sequence``
* ``collections.abc.MutableSequence`` and ``typing.MutableSequence``
* ``collections.abc.ByteString`` and ``typing.ByteString``
* ``collections.abc.MappingView`` and ``typing.MappingView``
* ``collections.abc.KeysView`` and ``typing.KeysView``
* ``collections.abc.ItemsView`` and ``typing.ItemsView``
* ``collections.abc.ValuesView`` and ``typing.ValuesView``
* ``contextlib.AbstractContextManager`` and ``typing.ContextManager`` (note the change in name)
* ``contextlib.AbstractAsyncContextManager`` and ``typing.AsyncContextManager`` (note the change in name)
* ``re.Pattern`` and ``typing.Pattern``
* ``re.Match`` and ``typing.Match``

The generic aliases in the ``typing`` module are considered deprecated
and type checkers may warn if they are used.

``Union`` and ``Optional``
--------------------------

Before Python 3.10 (:pep:`604`), Python did not support the ``|`` operator
for creating unions of types. Therefore, the ``typing.Union`` special form can also
be used to create union types. Type checkers should treat the two forms as equivalent.

In addition, the ``Optional`` special form provides a shortcut for a union with ``None``.

Examples:

* ``int | str`` is the same as ``Union[int, str]``
* ``int | str | range`` is the same as ``Union[int, str, range]``
* ``int | None`` is the same as ``Optional[int]`` and ``Union[int, None]``

``Unpack``
----------

:pep:`646`, which introduced ``TypeVarTuple`` into Python 3.11, also made two grammar
changes to support use of variadic generics, allowing use of the ``*`` operator in
index operations and in ``*args`` annotations. The ``Unpack[]`` operator was added to
support equivalent semantics on older Python versions. It should be treated as equivalent
to the ``*`` syntax. In particular, the following are equivalent:

* ``A[*Ts]`` is the same as ``A[Unpack[Ts]]``
* ``def f(*args: *Ts): ...`` is the same as ``def f(*args: Unpack[Ts]): ...``
