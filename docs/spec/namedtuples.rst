.. _`namedtuple`:

Named Tuples
============

As with tuples, named tuple classes require some special behaviors for type
checking.


Defining Named Tuples
---------------------

A named tuple class can be defined using a class syntax or a factory function
call.

Type checkers should support the class syntax::

    class Point(NamedTuple):
        x: int
        y: int
        units: str = "meters"

Fields must be annotated attributes - methods and un-annotated attributes are not
considered fields. Field names may not start with an underscore.

    class MyTuple(NamedTuple):
        x1 = 1  # Not a field
        def x2() -> None: pass  # Not a field
        _x3: int  # Type error: illegal field name

Regardless of whether the class syntax or factory function call is used to define
a named tuple, type checkers should synthesize a ``__new__`` method based on
the named tuple fields. This mirrors the runtime behavior. In the example
above, the synthesized ``__new__`` method would look like the following::

    def __new__(cls, x: int, y: int, units: str = "meters") -> Self:
        ...

The runtime implementation of ``NamedTuple`` enforces that fields with default
values must come after fields without default values. Type checkers should
likewise enforce this restriction::

    class Location(NamedTuple):
        altitude: float = 0.0
        latitude: float  # Type error (previous field has a default value)
        longitude: float

A named tuple class can be subclassed, but any fields added by the subclass
are not considered part of the named tuple type. Type checkers should enforce
that these newly-added fields do not conflict with the named tuple fields
in the base class::

    class PointWithName(Point):
        name: str  # OK
        x: int  # Type error (invalid override of named tuple field)

In Python 3.11 and newer, the class syntax supports generic named tuple classes.
Type checkers should support this::

    class Property[T](NamedTuple):
        name: str
        value: T

    reveal_type(Property("height", 3.4))  # Revealed type is Property[float]

``NamedTuple`` does not support multiple inheritance. Type checkers should
enforce this limitation::

    class Unit(NamedTuple, object):  # Type error
        name: str

The factory function call supports two variants: ``collections.namedtuple`` and
``typing.NamedTuple``. The latter provides a way to specify the types
of the fields in the tuple whereas the former does not. The ``namedtuple``
form allows fields to be specified as a tuple or list of strings or a single
string with fields separated by whitespace or commas. The ``NamedTuple``
functional form accepts an iterable of ``(name, type)`` pairs.
For the ``namedtuple`` form, all fields are assumed to be of type ``Any``.

A type checker may support the factory function call in its various forms::

    Point1 = namedtuple('Point1', ['x', 'y'])
    Point2 = namedtuple('Point2', ('x', 'y'))
    Point3 = namedtuple('Point3', 'x y')
    Point4 = namedtuple('Point4', 'x, y')

    Point5 = NamedTuple('Point5', [('x', int), ('y', int)])
    Point6 = NamedTuple('Point6', (('x', int), ('y', int)))

At runtime, the ``namedtuple`` function disallows field names that begin with
an underscore or are illegal Python identifiers, and either raises an exception
or replaces these fields with a parameter name of the form ``_N``. The behavior
depends on the value of the ``rename`` argument. Type checkers may replicate
this behavior statically::

    NT1 = namedtuple("NT1", ["a", "a"])  # Type error (duplicate field name)
    NT2 = namedtuple("NT2", ["abc", "def"], rename=False)  # Type error (illegal field name)
    NT3 = namedtuple("NT3", ["abc", "_d"], rename=False)  # Type error (illegal field name)

    NT4 = namedtuple("NT4", ["abc", "def"], rename=True)  # OK
    NT4(abc="", _1="")  # OK

    NT5 = namedtuple("NT5", ["abc", "_d"], rename=True)  # OK
    NT5(abc="", _1="")  # OK

The ``namedtuple`` function also supports a ``defaults`` keyword argument that
specifies default values for the fields. Type checkers may support this::

    NT4 = namedtuple("NT4", "a b c", defaults=(1, 2))
    NT4()  # Type error (too few arguments)
    NT4(1)  # OK


Named Tuple Usage
-----------------

The fields within a named tuple instance can be accessed by name using an
attribute access (``.``) operator. Type checkers should support this::

    p = Point(1, 2)
    assert_type(p.x, int)
    assert_type(p.units, str)

Like normal tuples, elements of a named tuple can also be accessed by index,
and type checkers should support this::

    assert_type(p[0], int)
    assert_type(p[2], str)

Type checkers should enforce that named tuple fields cannot be overwritten
or deleted::

    p.x = 3  # Type error
    p[0] = 3  # Type error
    del p.x  # Type error
    del p[0]  # Type error

Like regular tuples, named tuples can be unpacked. Type checkers should understand
this::

    x, y, units = p
    assert_type(x, int)
    assert_type(units, str)

    x, y = p  # Type error (too few values to unpack)


Assignability
-------------

A named tuple is :term:`assignable` to a ``tuple`` with a known length and
parameterized by types corresponding to the named tuple's individual field
types::

    p = Point(x=1, y=2, units="inches")
    v1: tuple[int, int, str] = p  # OK
    v2: tuple[Any, ...] = p  # OK
    v3: tuple[int, int] = p  # Type error (too few elements)
    v4: tuple[int, str, str] = p  # Type error (incompatible element type)

As with normal tuples, named tuples are covariant in their type parameters::

    v5: tuple[float, float, str] = p  # OK
