Enumerations
============

The ``enum.Enum`` class behaves differently from other Python classes in several 
ways that require special-case handling in type checkers. This section discusses
the Enum behaviors that should be supported by type checkers and others which
may be supported optionally. It is recommended that library and type stub
authors avoid using optional behaviors because these may not be supported
by some type checkers.


Enum Definition
---------------

Enum classes can be defined using a "class syntax" or a "function syntax".
The function syntax offers several ways to specify enum members: names passed
as individual arguments, a list or tuple of names, a string of
comma-delimited or space-delimited names, a list or tuple of tuples that contain
name/value pairs, and a dictionary of name/value items.

Type checkers should support the class syntax, but the function syntax (in
its various forms) is optional::

    class Color1(Enum): # Supported
        RED = 1
        GREEN = 2
        BLUE = 3

    Color2 = Enum('Color2', 'RED', 'GREEN', 'BLUE')  # Optional
    Color3 = Enum('Color3', ['RED', 'GREEN', 'BLUE'])  # Optional
    Color4 = Enum('Color4', ('RED', 'GREEN', 'BLUE'))  # Optional
    Color5 = Enum('Color5', 'RED, GREEN, BLUE')  # Optional
    Color6 = Enum('Color6', 'RED GREEN BLUE')  # Optional
    Color7 = Enum('Color7', [('RED': 1), ('GREEN': 2), ('BLUE': 3)])  # Optional
    Color8 = Enum('Color8', (('RED': 1), ('GREEN': 2), ('BLUE': 3)))  # Optional
    Color9 = Enum('Color9', {'RED': 1, 'GREEN': 2, 'BLUE': 3})  # Optional

Enum classes can also be defined using a subclass of ``enum.Enum`` or any class
that uses ``enum.EnumType`` (or a subclass thereof) as a metaclass. Note that
``enum.EnumType`` was named ``enum.EnumMeta`` prior to Python 3.11. Type
checkers should treat such classes as enums::

    class CustomEnum1(Enum):
        pass
    
    class Color7(CustomEnum1):  # Supported
        RED = 1
        GREEN = 2
        BLUE = 3

    class CustomEnumType(EnumType):
        pass
    
    class CustomEnum2(metaclass=CustomEnumType):
        pass

    class Color8(CustomEnum2):  # Supported
        RED = 1
        GREEN = 2
        BLUE = 3


Enum Behaviors
--------------

Enum classes are iterable and indexable, and they can be called with a value
to look up the enum member with that value. Type checkers should support these
behaviors::

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    for color in Color:
        reveal_type(color)  # Revealed type is 'Color'

    reveal_type(Color["RED"])  # Revealed type is 'Literal[Color.RED]' (or 'Color')
    reveal_type(Color(3))  # Revealed type is 'Literal[Color.BLUE]' (or 'Color')

Unlike most Python classes, Calling an enum class does not invoke its constructor.
Instead, the call performs a value-based lookup of an enum member.

An Enum class with one or more defined members cannot be subclassed. They are
implicitly "final". Type checkers should enforce this::

    class EnumWithNoMembers(Enum):
        pass

    class Shape(EnumWithNoMembers):  # OK (because no members are defined)
        SQUARE = 1
        CIRCLE = 2

    class ExtendedShape(Shape):  # Type checker error: Shape is implicitly final
        TRIANGLE = 3


Defining Members
----------------

When using the "class syntax", enum classes can define both members and
other (non-member) attributes. The ``EnumType`` metaclass applies a set
of rules to distinguish between members and non-members. Type checkers
should honor the most common of these rules. The lesser-used rules are
optional. Some of these rules may be impossible to evaluate and enforce
statically in cases where dynamic values are used.

* If an attribute is defined in the class body with a type annotation but
  with no assigned value, a type checker should assume this is a non-member
  attribute::

    class Pet(Enum):
        genus: str  # Non-member attribute
        species: str  # Non-member attribute

        CAT = 1  # Member attribute
        DOG = 2  # Member attribute

  Within a type stub, members can be defined using the actual runtime values,
  or a placeholder of ``...`` can be used::

    class Pet(Enum):
        genus: str  # Non-member attribute
        species: str  # Non-member attribute

        CAT = ...  # Member attribute
        DOG = ...  # Member attribute

* Members defined within an enum class should not include explicit type
  annotations. Type checkers should infer a literal type for all members.
  A type checker should report an error if a type annotation is used
  for an enum member because this type will be incorrect and misleading
  to readers of the code::

    class Pet(Enum):
        CAT = 1  # OK
        DOG: int = 2  # Type checker error

* Methods, callables, and descriptors (including properties) that are defined
  in the class are not treated as enum members by the ``EnumType`` metaclass
  and should likewise not be treated as enum members by a type checker::

    def identity(__x): return __x

    class Pet(Enum):
        CAT = 1  # Member attribute
        DOG = 2  # Member attribute
        
        converter = lambda __x: str(__x)  # Non-member attribute
        transform = identity  # Non-member attribute

        @property
        def species(self) -> str:  # Non-member property
            return "mammal"
        
        def speak(self) -> None:  # Non-member method
            print("meow" if self is Pet.CAT else "woof")


* If using Python 3.11 or newer, the ``enum.member`` and ``enum.nonmember``
  classes can be used to unambiguously distinguish members from non-members.
  Type checkers should support these classes::

    class Example(Enum):
        a = member(1)  # Member attribute
        b = nonmember(2)  # Non-member attribute

        @member
        def c(self) -> None:  # Member method
            pass

    reveal_type(Example.a)  # Revealed type is Literal[Example.a]
    reveal_type(Example.b)  # Revealed type is int
    reveal_type(Example.c)  # Revealed type is Literal[Example.c]


* An enum class can define a class symbol named ``_ignore_``. This can be a list
  of names or a string containing a space-delimited list of names that are
  deleted from the enum class at runtime. Type checkers may support this
  mechanism::

    class Pet(Enum):
        _ignore_ = "DOG FISH"
        CAT = 1  # Member attribute
        DOG = 2  # temporary variable, will be removed from the final enum class
        FISH = 3  # temporary variable, will be removed from the final enum class


Member Names
------------

All enum member objects have an attribute ``_name_`` that contains the member's
name. They also have a property ``name`` that returns the same name. Type
checkers may infer a literal type for the name of a member::

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    reveal_type(Color.RED._name_)  # Revealed type is Literal["RED"] (or str)
    reveal_type(Color.RED.name)  # Revealed type is Literal["RED"] (or str)

    def func1(red_or_blue: Literal[Color.RED, Color.BLUE]):
        reveal_type(red_or_blue.name)  # Revealed type is Literal["RED", "BLUE"] (or str)

    def func2(any_color: Color):
        reveal_type(any_color.name)  # Revealed type is Literal["RED", "BLUE", "GREEN"] (or str)


Member Values
-------------

All enum member objects have an attribute ``_value_`` that contains the member's
value. They also have a property ``value`` that returns the same value. Type
checkers may infer the type of a member's value::

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    reveal_type(Color.RED._value_)  # Revealed type is Literal[1] (or int or object or Any)
    reveal_type(Color.RED.value)  # Revealed type is Literal[1] (or int or object or Any)

    def func1(red_or_blue: Literal[Color.RED, Color.BLUE]):
        reveal_type(red_or_blue.value)  # Revealed type is Literal[1, 2] (or int or object or Any)

    def func2(any_color: Color):
        reveal_type(any_color.value)  # Revealed type is Literal[1, 2, 3] (or int or object or Any)


The value of ``_value_`` can be assigned in a constructor method. This technique
is sometimes used to initialize both the member value and non-member attributes.
If the value assigned in the class body is a tuple, the unpacked tuple value is
passed to the constructor. Type checkers may validate consistency between assigned
tuple values and the constructor signature::

    class Planet(Enum):
        def __init__(self, value: int, mass: float, radius: float):
            self._value_ = value
            self.mass = mass
            self.radius = radius

        MERCURY = (1, 3.303e+23, 2.4397e6)
        VENUS = (2, 4.869e+24, 6.0518e6)
        EARTH = (3, 5.976e+24, 6.37814e6)
        MARS = (6.421e+23, 3.3972e6)  # Type checker error (optional)
        JUPITER = 5  # Type checker error (optional)

    reveal_type(Planet.MERCURY.value)  # Revealed type is Literal[1] (or int or object or Any)


The class ``enum.auto`` and method ``_generate_next_value_`` can be used within
an enum class to automatically generate values for enum members. Type checkers
may support these to infer literal types for member values::

    class Color(Enum):
        RED = auto()
        GREEN = auto()
        BLUE = auto()

    reveal_type(Color.RED.value)  # Revealed type is Literal[1] (or int or object or Any)


If an enum class provides an explicit type annotation for ``_value_``, type
checkers should enforce this declared type when values are assigned to
``_value_``::

    class Color(Enum):
        _value_: int
        RED = 1 # OK
        GREEN = "green"  # Type error

    class Planet(Enum):
        _value_: str

        def __init__(self, value: int, mass: float, radius: float):
            self._value_ = value # Type error

        MERCURY = (1, 3.303e+23, 2.4397e6)

If the literal values for enum members are not supplied, as they sometimes
are not within a type stub file, a type checker can use the type of the
``_value_`` attribute::

    class ColumnType(Enum):
        _value_: int
        DORIC = ...
        IONIC = ...
        CORINTHIAN = ...
    
    reveal_type(ColumnType.DORIC.value)  # Revealed type is int (or object or Any)


Enum Literal Expansion
----------------------

From the perspective of the type system, an enum class is equivalent to the union
of the literal members within that enum. Because of this equivalency, the
two types may be used interchangeably. Type checkers may therefore expand
an enum type into a union of literal values during type narrowing and
exhaustion detection::

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3
    
    def print_color1(c: Color):
        if c is Color.RED or c is Color.BLUE:
            print("red or blue")
        else:
            reveal_type(c)  # Revealed type is Literal[Color.GREEN]

    def print_color2(c: Color):
        match c:
            case Color.RED | Color.BLUE:
                print("red or blue")
            case Color.GREEN:
                print("green")
            case _:
                reveal_type(c)  # Revealed type is Never


Likewise, a type checker should treat a complete union of all literal members
as compatible with the enum type::

    class Answer(Enum):
        Yes = 1
        No = 2

    def func(val: object) -> Answer:
        if val is not Answer.Yes and val is not Answer.No:
            raise ValueError("Invalid value")
        reveal_type(val)  # Revealed type is Answer (or Literal[Answer.Yes, Answer.No])
        return val  # OK
