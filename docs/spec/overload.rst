``@overload``
=============

The ``@overload`` decorator allows describing functions and methods
that support multiple different combinations of argument types.  This
pattern is used frequently in builtin modules and types.  For example,
the ``__getitem__()`` method of the ``bytes`` type can be described as
follows::

  from typing import overload

  class bytes:
      ...
      @overload
      def __getitem__(self, i: int) -> int: ...
      @overload
      def __getitem__(self, s: slice) -> bytes: ...

This description is more precise than would be possible using unions
(which cannot express the relationship between the argument and return
types)::

  class bytes:
      ...
      def __getitem__(self, a: int | slice) -> int | bytes: ...

Another example where ``@overload`` comes in handy is the type of the
builtin ``map()`` function, which takes a different number of
arguments depending on the type of the callable::

  from typing import TypeVar, overload
  from collections.abc import Callable, Iterable, Iterator

  T1 = TypeVar('T1')
  T2 = TypeVar('T2')
  S = TypeVar('S')

  @overload
  def map(func: Callable[[T1], S], iter1: Iterable[T1]) -> Iterator[S]: ...
  @overload
  def map(func: Callable[[T1, T2], S],
          iter1: Iterable[T1], iter2: Iterable[T2]) -> Iterator[S]: ...
  # ... and we could add more items to support more than two iterables

Note that we could also easily add items to support ``map(None, ...)``::

  @overload
  def map(func: None, iter1: Iterable[T1]) -> Iterable[T1]: ...
  @overload
  def map(func: None,
          iter1: Iterable[T1],
          iter2: Iterable[T2]) -> Iterable[tuple[T1, T2]]: ...

Uses of the ``@overload`` decorator as shown above are suitable for
stub files.  In regular modules, a series of ``@overload``-decorated
definitions must be followed by exactly one
non-``@overload``-decorated definition (for the same function/method).
The ``@overload``-decorated definitions are for the benefit of the
type checker only, since they will be overwritten by the
non-``@overload``-decorated definition, while the latter is used at
runtime but should be ignored by a type checker.  At runtime, calling
a ``@overload``-decorated function directly will raise
``NotImplementedError``.  Here's an example of a non-stub overload
that can't easily be expressed using a union or a type variable::

  @overload
  def utf8(value: None) -> None:
      pass
  @overload
  def utf8(value: bytes) -> bytes:
      pass
  @overload
  def utf8(value: unicode) -> bytes:
      pass
  def utf8(value):
      <actual implementation>

A constrained ``TypeVar`` type can often be used instead of using the
``@overload`` decorator.  For example, the definitions of ``concat1``
and ``concat2`` in this stub file are equivalent::

  from typing import TypeVar

  AnyStr = TypeVar('AnyStr', str, bytes)

  def concat1(x: AnyStr, y: AnyStr) -> AnyStr: ...

  @overload
  def concat2(x: str, y: str) -> str: ...
  @overload
  def concat2(x: bytes, y: bytes) -> bytes: ...

Some functions, such as ``map`` or ``bytes.__getitem__`` above, can't
be represented precisely using type variables. We
recommend that ``@overload`` is only used in cases where a type
variable is not sufficient.

Another important difference between type variables such as ``AnyStr``
and using ``@overload`` is that the prior can also be used to define
constraints for generic class type parameters.  For example, the type
parameter of the generic class ``typing.IO`` is constrained (only
``IO[str]``, ``IO[bytes]`` and ``IO[Any]`` are valid)::

  class IO(Generic[AnyStr]): ...
