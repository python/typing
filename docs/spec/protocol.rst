.. _protocols:

Protocols
---------

(Originally specified in :pep:`544`.)

Terminology
^^^^^^^^^^^

The term *protocols* is used for some types supporting :term:`structural`
subtyping. The reason is that the term *iterator protocol*,
for example, is widely understood in the community, and coming up with
a new term for this concept in a statically typed context would just create
confusion.

This has the drawback that the term *protocol* becomes overloaded with
two subtly different meanings: the first is the traditional, well-known but
slightly fuzzy concept of protocols such as iterator; the second is the more
explicitly defined concept of protocols in statically typed code.
The distinction is not important most of the time, and in other
cases we can just add a qualifier such as *protocol classes*
when referring to the static type concept.

If a class includes a protocol in its MRO, the class is called an *explicit*
subclass of the protocol. If a class defines all attributes and methods of a
protocol with types that are :term:`assignable` to the types of the protocol's
attributes and methods, it is said to implement the protocol and to be
assignable to the protocol. If a class is assignable to a protocol but the
protocol is not included in the MRO, the class is *implicitly* assignable to
the protocol. (Note that one can explicitly subclass a protocol and still not
implement it if a protocol attribute is set to ``None`` in the subclass. See
Python :py:ref:`data model <specialnames>` for details.)

The attributes (variables and methods) of a protocol that are mandatory for
another class for it to be assignable to the protocol are called "protocol
members".

.. _protocol-definition:

Defining a protocol
^^^^^^^^^^^^^^^^^^^

Protocols are defined by including a :term:`special form` ``typing.Protocol``
(an instance of ``abc.ABCMeta``) in the base classes list, typically
at the end of the list. Here is a simple example::

  from typing import Protocol

  class SupportsClose(Protocol):
      def close(self) -> None:
          ...

Now if one defines a class ``Resource`` with a ``close()`` method whose type
signature is :term:`assignable` to ``SupportsClose.close``, it would implicitly
be assignable to ``SupportsClose``, since :term:`structural` assignability is
used for protocol types::

  class Resource:
      ...
      def close(self) -> None:
          self.file.close()
          self.lock.release()

Apart from a few restrictions explicitly mentioned below, protocol types can
be used in every context where normal types can::

  def close_all(things: Iterable[SupportsClose]) -> None:
      for t in things:
          t.close()

  f = open('foo.txt')
  r = Resource()
  close_all([f, r])  # OK!
  close_all([1])     # Error: 'int' has no 'close' method

Note that both the user-defined class ``Resource`` and the built-in ``IO`` type
(the return type of ``open()``) are assignable to ``SupportsClose``, because
each provides a ``close()`` method with an assignable type signature.


Protocol members
^^^^^^^^^^^^^^^^

All methods defined in the protocol class body are protocol members, both
normal and decorated with ``@abstractmethod``. If any parameters of a
protocol method are not annotated, then their types are assumed to be ``Any``
(see :ref:`"The meaning of annotations" <missing-annotations>`). Bodies of protocol methods are type checked.
An abstract method that should not be called via ``super()`` ought to raise
``NotImplementedError``. Example::

  from typing import Protocol
  from abc import abstractmethod

  class Example(Protocol):
      def first(self) -> int:     # This is a protocol member
          return 42

      @abstractmethod
      def second(self) -> int:    # Method without a default implementation
          raise NotImplementedError

Static methods, class methods, and properties are equally allowed
in protocols.

To define a protocol variable, one can use variable
annotations in the class body. Additional attributes *only* defined in
the body of a method by assignment via ``self`` are not allowed. The rationale
for this is that the protocol class implementation is often not shared by
subtypes, so the interface should not depend on the default implementation.
Examples::

  from typing import Protocol

  class Template(Protocol):
      name: str        # This is a protocol member
      value: int = 0   # This one too (with default)

      def method(self) -> None:
          self.temp: list[int] = [] # Error in type checker

  class Concrete:
      def __init__(self, name: str, value: int) -> None:
          self.name = name
          self.value = value

      def method(self) -> None:
          return

  var: Template = Concrete('value', 42)  # OK

To distinguish between protocol class variables and protocol instance
variables, the special :ref:`ClassVar <classvar>` annotation should be used.
By default, protocol variables as defined above are considered
readable and writable. To define a read-only protocol variable, one can use
an (abstract) property.


Explicitly declaring implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To explicitly declare that a certain class implements a given protocol,
it can be used as a regular base class. In this case a class could use
default implementations of protocol members. Static analysis tools are
expected to automatically detect that a class implements a given protocol.
So while it's possible to subclass a protocol explicitly, it's *not necessary*
to do so for the sake of type-checking.

The default implementations cannot be used if the assignable-to relationship is
implicit and only :term:`structural` -- the semantics of inheritance is not
changed. Examples::

    class PColor(Protocol):
        @abstractmethod
        def draw(self) -> str:
            ...
        def complex_method(self) -> int:
            # some complex code here

    class NiceColor(PColor):
        def draw(self) -> str:
            return "deep blue"

    class BadColor(PColor):
        def draw(self) -> str:
            return super().draw()  # Error, no default implementation

    class ImplicitColor:   # Note no 'PColor' base here
        def draw(self) -> str:
            return "probably gray"
        def complex_method(self) -> int:
            # class needs to implement this

    nice: NiceColor
    another: ImplicitColor

    def represent(c: PColor) -> None:
        print(c.draw(), c.complex_method())

    represent(nice) # OK
    represent(another) # Also OK

Note that there is little difference between explicitly subclassing and
implicitly implementing the protocol; the main benefit of explicit subclassing
is to get some protocol methods "for free". In addition, type checkers can
statically verify that the class actually implements the protocol correctly::

    class RGB(Protocol):
        rgb: tuple[int, int, int]

        @abstractmethod
        def intensity(self) -> int:
            return 0

    class Point(RGB):
        def __init__(self, red: int, green: int, blue: str) -> None:
            self.rgb = red, green, blue  # Error, 'blue' must be 'int'

        # Type checker might warn that 'intensity' is not defined

A class can explicitly inherit from multiple protocols and also from normal
classes. In this case methods are resolved using normal MRO and a type checker
verifies that all member assignability is correct. The semantics of
``@abstractmethod`` is not changed; all of them must be implemented by an
explicit subclass before it can be instantiated.


Merging and extending protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The general philosophy is that protocols are mostly like regular ABCs, but a
static type checker will handle them specially. Subclassing a protocol class
would not turn the subclass into a protocol unless it also has
``typing.Protocol`` as an explicit base class. Without this base, the class is
"downgraded" to a regular ABC that cannot be used with :term:`structural`
subtyping. The rationale for this rule is that we don't want to accidentally
have some class act as a protocol just because one of its base classes happens
to be one. We still slightly prefer :term:`nominal` subtyping over structural
subtyping in the static typing world.

A subprotocol can be defined by having *both* one or more protocols as
immediate base classes and also having ``typing.Protocol`` as an immediate
base class::

  from typing import Protocol
  from collections.abc import Sized

  class SizedAndClosable(Sized, Protocol):
      def close(self) -> None:
          ...

Now the protocol ``SizedAndClosable`` is a protocol with two methods,
``__len__`` and ``close``. If one omits ``Protocol`` in the base class list,
this would be a regular (non-protocol) class that must implement ``Sized``.
Alternatively, one can implement ``SizedAndClosable`` protocol by merging
the ``SupportsClose`` protocol from the example in the `protocol-definition`_ section
with ``typing.Sized``::

  from collections.abc import Sized

  class SupportsClose(Protocol):
      def close(self) -> None:
          ...

  class SizedAndClosable(Sized, SupportsClose, Protocol):
      pass

The two definitions of ``SizedAndClosable`` are equivalent. Subclass
relationships between protocols are not meaningful when considering
assignability, since :term:`structural` :term:`assignability <assignable>` is
the criterion, not the MRO.

If ``Protocol`` is included in the base class list, all the other base classes
must be protocols. A protocol can't extend a regular class.
Note that rules around explicit subclassing are different
from regular ABCs, where abstractness is simply defined by having at least one
abstract method being unimplemented. Protocol classes must be marked
*explicitly*.

.. _`generic-protocols`:

Generic protocols
^^^^^^^^^^^^^^^^^

Generic protocols are important. For example, ``SupportsAbs``, ``Iterable``
and ``Iterator`` are generic protocols. They are defined similar to normal
non-protocol generic types::

  class Iterable(Protocol[T]):
      @abstractmethod
      def __iter__(self) -> Iterator[T]:
          ...

``Protocol[T, S, ...]`` is allowed as a shorthand for
``Protocol, Generic[T, S, ...]``. It is an error to combine
``Protocol[T, S, ...]`` with ``Generic[T, S, ...]``, or with the new syntax for
generic classes in Python 3.12 and above::

  class Iterable(Protocol[T], Generic[T]):   # INVALID
      ...

  class Iterable[T](Protocol[T]):   # INVALID
      ...

User-defined generic protocols support explicitly declared variance.
Type checkers will warn if the inferred variance is different from
the declared variance. Examples::

  T = TypeVar('T')
  T_co = TypeVar('T_co', covariant=True)
  T_contra = TypeVar('T_contra', contravariant=True)

  class Box(Protocol[T_co]):
      def content(self) -> T_co:
          ...

  box: Box[float]
  second_box: Box[int]
  box = second_box  # This is OK due to the covariance of 'Box'.

  class Sender(Protocol[T_contra]):
      def send(self, data: T_contra) -> int:
          ...

  sender: Sender[float]
  new_sender: Sender[int]
  new_sender = sender  # OK, 'Sender' is contravariant.

  class Proto(Protocol[T]):
      attr: T  # this class is invariant, since it has a mutable attribute

  var: Proto[float]
  another_var: Proto[int]
  var = another_var  # Error! 'Proto[float]' is not assignable to 'Proto[int]'.

Note that unlike nominal classes, de facto covariant protocols cannot be
declared as invariant, since this can break transitivity of subtyping.
For example::

  T = TypeVar('T')

  class AnotherBox(Protocol[T]):  # Error, this protocol is covariant in T,
      def content(self) -> T:     # not invariant.
          ...


Recursive protocols
^^^^^^^^^^^^^^^^^^^

Recursive protocols are also supported. Forward references to the protocol
class names can be :ref:`given as strings <forward-references>`. Recursive
protocols are useful for representing self-referential data structures
like trees in an abstract fashion::

  class Traversable(Protocol):
      def leaves(self) -> Iterable['Traversable']:
          ...

Note that for recursive protocols, a class is considered assignable to
the protocol in situations where the decision depends on itself.
Continuing the previous example::

  class SimpleTree:
      def leaves(self) -> list['SimpleTree']:
          ...

  root: Traversable = SimpleTree()  # OK

  class Tree(Generic[T]):
      def leaves(self) -> list['Tree[T]']:
          ...

  def walk(graph: Traversable) -> None:
      ...
  tree: Tree[float] = Tree()
  walk(tree)  # OK, 'Tree[float]' is assignable to 'Traversable'


Self-types in protocols
^^^^^^^^^^^^^^^^^^^^^^^

The self-types in protocols follow the
:ref:`rules for other methods <annotating-methods>`. For example::

  C = TypeVar('C', bound='Copyable')
  class Copyable(Protocol):
      def copy(self: C) -> C:

  class One:
      def copy(self) -> 'One':
          ...

  T = TypeVar('T', bound='Other')
  class Other:
      def copy(self: T) -> T:
          ...

  c: Copyable
  c = One()  # OK
  c = Other()  # Also OK

Assignability relationships with other types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Protocols cannot be instantiated, so there are no values whose
runtime type is a protocol. For variables and parameters with protocol types,
assignability relationships are subject to the following rules:

* A protocol is never assignable to a concrete type.
* A concrete type ``X`` is assignable to a protocol ``P`` if and only if ``X``
  implements all protocol members of ``P`` with assignable types. In other
  words, :term:`assignability <assignable>` with respect to a protocol is
  always :term:`structural`.
* A protocol ``P1`` is assignable to another protocol ``P2`` if ``P1`` defines
  all protocol members of ``P2`` with assignable types.

Generic protocol types follow the same rules of variance as non-protocol
types. Protocol types can be used in all contexts where any other types
can be used, such as in unions, ``ClassVar``, type variables bounds, etc.
Generic protocols follow the rules for generic abstract classes, except for
using structural assignability instead of assignability defined by
inheritance relationships.

Static type checkers will recognize protocol implementations, even if the
corresponding protocols are *not imported*::

  # file lib.py
  from collections.abc import Sized

  T = TypeVar('T', contravariant=True)
  class ListLike(Sized, Protocol[T]):
      def append(self, x: T) -> None:
          pass

  def populate(lst: ListLike[int]) -> None:
      ...

  # file main.py
  from lib import populate  # Note that ListLike is NOT imported

  class MockStack:
      def __len__(self) -> int:
          return 42
      def append(self, x: int) -> None:
          print(x)

  populate([1, 2, 3])    # Passes type check
  populate(MockStack())  # Also OK


Unions and intersections of protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Unions of protocol classes behaves the same way as for non-protocol
classes. For example::

  from typing import Protocol

  class Exitable(Protocol):
      def exit(self) -> int:
          ...
  class Quittable(Protocol):
      def quit(self) -> int | None:
          ...

  def finish(task: Exitable | Quittable) -> int:
      ...
  class DefaultJob:
      ...
      def quit(self) -> int:
          return 0
  finish(DefaultJob()) # OK

One can use multiple inheritance to define an intersection of protocols.
Example::

  from collections.abc import Iterable, Hashable

  class HashableFloats(Iterable[float], Hashable, Protocol):
      pass

  def cached_func(args: HashableFloats) -> float:
      ...
  cached_func((1, 2, 3)) # OK, tuple is both hashable and iterable


``type[]`` and class objects vs protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Variables and parameters annotated with ``type[Proto]`` accept only concrete
(non-protocol) :term:`consistent subtypes <consistent subtype>` of ``Proto``.
The main reason for this is to allow instantiation of parameters with such
types. For example::

  class Proto(Protocol):
      @abstractmethod
      def meth(self) -> int:
          ...
  class Concrete:
      def meth(self) -> int:
          return 42

  def fun(cls: type[Proto]) -> int:
      return cls().meth() # OK
  fun(Proto)              # Error
  fun(Concrete)           # OK

The same rule applies to variables::

  var: Type[Proto]
  var = Proto    # Error
  var = Concrete # OK
  var().meth()   # OK

Assigning an ABC or a protocol class to a variable is allowed if it is
not explicitly typed, and such assignment creates a type alias.
For normal (non-abstract) classes, the behavior of ``type[]`` is
not changed.

A class object is considered an implementation of a protocol if accessing
all members on it results in types assignable to the types of the protocol members.
For example::

  from typing import Any, Protocol

  class ProtoA(Protocol):
      def meth(self, x: int) -> int: ...
  class ProtoB(Protocol):
      def meth(self, obj: Any, x: int) -> int: ...

  class C:
      def meth(self, x: int) -> int: ...

  a: ProtoA = C  # Type check error, signatures don't match!
  b: ProtoB = C  # OK


``NewType()`` and type aliases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Protocols are essentially anonymous. To emphasize this point, static type
checkers might refuse protocol classes inside ``NewType()`` to avoid an
illusion that a distinct type is provided::

  from typing import NewType, Protocol
  from collections.abc import Iterator

  class Id(Protocol):
      code: int
      secrets: Iterator[bytes]

  UserId = NewType('UserId', Id)  # Error, can't provide distinct type

In contrast, type aliases are fully supported, including generic type
aliases::

  from typing import TypeVar
  from collections.abc import Reversible, Iterable, Sized

  T = TypeVar('T')
  class SizedIterable(Iterable[T], Sized, Protocol):
      pass
  CompatReversible = Reversible[T] | SizedIterable[T]


Modules as implementations of protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A module object is accepted where a protocol is expected if the public
interface of the given module is assignable to the expected protocol.
For example::

  # file default_config.py
  timeout = 100
  one_flag = True
  other_flag = False

  # file main.py
  import default_config
  from typing import Protocol

  class Options(Protocol):
      timeout: int
      one_flag: bool
      other_flag: bool

  def setup(options: Options) -> None:
      ...

  setup(default_config)  # OK

To determine assignability of module level functions, the ``self`` argument
of the corresponding protocol methods is dropped. For example::

  # callbacks.py
  def on_error(x: int) -> None:
      ...
  def on_success() -> None:
      ...

  # main.py
  import callbacks
  from typing import Protocol

  class Reporter(Protocol):
      def on_error(self, x: int) -> None:
          ...
      def on_success(self) -> None:
          ...

  rp: Reporter = callbacks  # Passes type check

.. _`runtime-checkable`:

``@runtime_checkable`` decorator and narrowing types by ``isinstance()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default semantics is that ``isinstance()`` and ``issubclass()`` fail
for protocol types. This is in the spirit of duck typing -- protocols
basically would be used to model duck typing statically, not explicitly
at runtime.

However, it should be possible for protocol types to implement custom
instance and class checks when this makes sense, similar to how ``Iterable``
and other ABCs in ``collections.abc`` and ``typing`` already do it,
but this is limited to non-generic and unsubscripted generic protocols
(``Iterable`` is statically equivalent to ``Iterable[Any]``).
The ``typing`` module will define a special ``@runtime_checkable`` class decorator
that provides the same semantics for class and instance checks as for
``collections.abc`` classes, essentially making them "runtime protocols"::

  from typing import runtime_checkable, Protocol

  @runtime_checkable
  class SupportsClose(Protocol):
      def close(self):
          ...

  assert isinstance(open('some/file'), SupportsClose)

Note that instance checks are not 100% reliable statically, which is why
this behavior is opt-in.
The most type checkers can do is to treat ``isinstance(obj, Iterator)``
roughly as a simpler way to write
``hasattr(x, '__iter__') and hasattr(x, '__next__')``. To minimize
the risks for this feature, the following rules are applied.

**Definitions**:

* *Data and non-data protocols*: A protocol is called a non-data protocol
  if it only contains methods as members (for example ``Sized``,
  ``Iterator``, etc). A protocol that contains at least one non-method member
  (like ``x: int``) is called a data protocol.
* *Unsafe overlap*: A type ``X`` is called unsafely overlapping with a protocol
  ``P``, if ``X`` is not assignable to ``P``, but it is assignable to the
  type-erased version of ``P`` where all members have type ``Any``. In
  addition, if at least one element of a union unsafely overlaps with a
  protocol ``P``, then the whole union is unsafely overlapping with ``P``.

**Specification**:

* A protocol can be used as a second argument in ``isinstance()`` and
  ``issubclass()`` only if it is explicitly opt-in by ``@runtime_checkable``
  decorator. This requirement exists because protocol checks are not type safe
  in case of dynamically set attributes, and because type checkers can only prove
  that an ``isinstance()`` check is safe only for a given class, not for all its
  subclasses.
* ``isinstance()`` can be used with both data and non-data protocols, while
  ``issubclass()`` can be used only with non-data protocols. This restriction
  exists because some data attributes can be set on an instance in constructor
  and this information is not always available on the class object.
* Type checkers should reject an ``isinstance()`` or ``issubclass()`` call, if
  there is an unsafe overlap between the type of the first argument and
  the protocol.
* Type checkers should be able to select a correct element from a union after
  a safe ``isinstance()`` or ``issubclass()`` call. For narrowing from non-union
  types, type checkers can use their best judgement (this is intentionally
  unspecified, since a precise specification would require intersection types).
