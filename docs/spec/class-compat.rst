Class type compatibility
========================

``ClassVar``
------------

(Originally specified in :pep:`526`.)

A covariant type ``ClassVar[T_co]`` exists in the ``typing``
module. It accepts only a single argument that should be a valid type,
and is used to annotate class variables that should not be set on class
instances. This restriction is ensured by static checkers,
but not at runtime.

Type annotations can be used to annotate class and instance variables
in class bodies and methods. In particular, the value-less notation ``a: int``
allows one to annotate instance variables that should be initialized
in ``__init__`` or ``__new__``. The syntax is as follows::

  class BasicStarship:
      captain: str = 'Picard'               # instance variable with default
      damage: int                           # instance variable without default
      stats: ClassVar[dict[str, int]] = {}  # class variable

Here ``ClassVar`` is a special class defined by the typing module that
indicates to the static type checker that this variable should not be
set on instances.

Note that a ``ClassVar`` parameter cannot include any type variables, regardless
of the level of nesting: ``ClassVar[T]`` and ``ClassVar[list[set[T]]]`` are
both invalid if ``T`` is a type variable.

This could be illustrated with a more detailed example. In this class::

  class Starship:
      captain = 'Picard'
      stats = {}

      def __init__(self, damage, captain=None):
          self.damage = damage
          if captain:
              self.captain = captain  # Else keep the default

      def hit(self):
          Starship.stats['hits'] = Starship.stats.get('hits', 0) + 1

``stats`` is intended to be a class variable (keeping track of many different
per-game statistics), while ``captain`` is an instance variable with a default
value set in the class. This difference might not be seen by a type
checker: both get initialized in the class, but ``captain`` serves only
as a convenient default value for the instance variable, while ``stats``
is truly a class variable -- it is intended to be shared by all instances.

Since both variables happen to be initialized at the class level, it is
useful to distinguish them by marking class variables as annotated with
types wrapped in ``ClassVar[...]``. In this way a type checker may flag
accidental assignments to attributes with the same name on instances.

For example, annotating the discussed class::

  class Starship:
      captain: str = 'Picard'
      damage: int
      stats: ClassVar[dict[str, int]] = {}

      def __init__(self, damage: int, captain: str = None):
          self.damage = damage
          if captain:
              self.captain = captain  # Else keep the default

      def hit(self):
          Starship.stats['hits'] = Starship.stats.get('hits', 0) + 1

  enterprise_d = Starship(3000)
  enterprise_d.stats = {} # Flagged as error by a type checker
  Starship.stats = {} # This is OK

As a matter of convenience (and convention), instance variables can be
annotated in ``__init__`` or other methods, rather than in the class::

  from typing import Generic, TypeVar
  T = TypeVar('T')

  class Box(Generic[T]):
      def __init__(self, content):
          self.content: T = content

``@override``
-------------

(Originally specified by :pep:`698`.)

When type checkers encounter a method decorated with ``@typing.override`` they
should treat it as a type error unless that method is overriding a compatible
method or attribute in some ancestor class.


.. code-block:: python

    from typing import override

    class Parent:
        def foo(self) -> int:
            return 1

        def bar(self, x: str) -> str:
            return x

    class Child(Parent):
        @override
        def foo(self) -> int:
            return 2

        @override
        def baz() -> int:  # Type check error: no matching signature in ancestor
            return 1


The ``@override`` decorator should be permitted anywhere a type checker
considers a method to be a valid override, which typically includes not only
normal methods but also ``@property``, ``@staticmethod``, and ``@classmethod``.


Strict Enforcement Per-Project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We believe that ``@override`` is most useful if checkers also allow developers
to opt into a strict mode where methods that override a parent class are
required to use the decorator. Strict enforcement should be opt-in for backward
compatibility.
