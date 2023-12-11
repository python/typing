Callables
=========

Argument defaults
-----------------

It may be useful to declare an argument as having a default
without specifying the actual default value.  For example::

  def foo(x: AnyStr, y: AnyStr = ...) -> AnyStr: ...

What should the default value look like?  Any of the options ``""``,
``b""`` or ``None`` fails to satisfy the type constraint.

In such cases the default value may be specified as a literal
ellipsis, i.e. the above example is literally what you would write.

Annotating ``*args`` and ``**kwargs``
-------------------------------------

Type annotation on variadic positional arguments
(``*args``) and keyword arguments (``**kwargs``) refer to
the types of individual arguments, not to the type of the
entire collection (except if ``Unpack`` is used).

Therefore, the definition::

  def foo(*args: str, **kwds: int): ...

is acceptable and it means that the function accepts an
arbitrary number of positional arguments of type ``str``
and an arbitrary number of keyword arguments of type ``int``.
For example, all of the following
represent function calls with valid types of arguments::

  foo('a', 'b', 'c')
  foo(x=1, y=2)
  foo('', z=0)

In the body of function ``foo``, the type of variable ``args`` is
deduced as ``tuple[str, ...]`` and the type of variable ``kwds``
is ``dict[str, int]``.

.. _unpack-kwargs:

``Unpack`` for keyword arguments
--------------------------------

``typing.Unpack`` has two use cases in the type system:

* As introduced by :pep:`646`, a backward-compatible form for certain operations
  involving variadic generics. See the section on ``TypeVarTuple`` for details.
* As introduced by :pep:`692`, a way to annotate the ``**kwargs`` of a function.

This second usage is described in this section. The following example::

    from typing import TypedDict, Unpack

    class Movie(TypedDict):
        name: str
        year: int

    def foo(**kwargs: Unpack[Movie]) -> None: ...

means that the ``**kwargs`` comprise two keyword arguments specified by
``Movie`` (i.e. a ``name`` keyword of type ``str`` and a ``year`` keyword of
type ``int``). This indicates that the function should be called as follows::

    kwargs: Movie = {"name": "Life of Brian", "year": 1979}

    foo(**kwargs)                               # OK!
    foo(name="The Meaning of Life", year=1983)  # OK!

When ``Unpack`` is used, type checkers treat ``kwargs`` inside the
function body as a ``TypedDict``::

    def foo(**kwargs: Unpack[Movie]) -> None:
        assert_type(kwargs, Movie)  # OK!


Using the new annotation will not have any runtime effect - it should only be
taken into account by type checkers. Any mention of errors in the following
sections relates to type checker errors.

Function calls with standard dictionaries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Passing a dictionary of type ``dict[str, object]`` as a ``**kwargs`` argument
to a function that has ``**kwargs`` annotated with ``Unpack`` must generate a
type checker error. On the other hand, the behaviour for functions using
standard, untyped dictionaries can depend on the type checker. For example::

    def foo(**kwargs: Unpack[Movie]) -> None: ...

    movie: dict[str, object] = {"name": "Life of Brian", "year": 1979}
    foo(**movie)  # WRONG! Movie is of type dict[str, object]

    typed_movie: Movie = {"name": "The Meaning of Life", "year": 1983}
    foo(**typed_movie)  # OK!

    another_movie = {"name": "Life of Brian", "year": 1979}
    foo(**another_movie)  # Depends on the type checker.

Keyword collisions
^^^^^^^^^^^^^^^^^^

A ``TypedDict`` that is used to type ``**kwargs`` could potentially contain
keys that are already defined in the function's signature. If the duplicate
name is a standard parameter, an error should be reported by type checkers.
If the duplicate name is a positional-only parameter, no errors should be
generated. For example::

    def foo(name, **kwargs: Unpack[Movie]) -> None: ...     # WRONG! "name" will
                                                            # always bind to the
                                                            # first parameter.

    def foo(name, /, **kwargs: Unpack[Movie]) -> None: ...  # OK! "name" is a
                                                            # positional-only parameter,
                                                            # so **kwargs can contain
                                                            # a "name" keyword.

Required and non-required keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default all keys in a ``TypedDict`` are required. This behaviour can be
overridden by setting the dictionary's ``total`` parameter as ``False``.
Moreover, :pep:`655` introduced new type qualifiers - ``typing.Required`` and
``typing.NotRequired`` - that enable specifying whether a particular key is
required or not::

    class Movie(TypedDict):
        title: str
        year: NotRequired[int]

When using a ``TypedDict`` to type ``**kwargs`` all of the required and
non-required keys should correspond to required and non-required function
keyword parameters. Therefore, if a required key is not supported by the
caller, then an error must be reported by type checkers.

Assignment
^^^^^^^^^^

Assignments of a function typed with ``**kwargs: Unpack[Movie]`` and
another callable type should pass type checking only if they are compatible.
This can happen for the scenarios described below.

Source and destination contain ``**kwargs``
"""""""""""""""""""""""""""""""""""""""""""

Both destination and source functions have a ``**kwargs: Unpack[TypedDict]``
parameter and the destination function's ``TypedDict`` is assignable to the
source function's ``TypedDict`` and the rest of the parameters are
compatible::

    class Animal(TypedDict):
        name: str

    class Dog(Animal):
        breed: str

    def accept_animal(**kwargs: Unpack[Animal]): ...
    def accept_dog(**kwargs: Unpack[Dog]): ...

    accept_dog = accept_animal  # OK! Expression of type Dog can be
                                # assigned to a variable of type Animal.

    accept_animal = accept_dog  # WRONG! Expression of type Animal
                                # cannot be assigned to a variable of type Dog.

.. _PEP 692 assignment dest no kwargs:

Source contains ``**kwargs`` and destination doesn't
""""""""""""""""""""""""""""""""""""""""""""""""""""

The destination callable doesn't contain ``**kwargs``, the source callable
contains ``**kwargs: Unpack[TypedDict]`` and the destination function's keyword
arguments are assignable to the corresponding keys in source function's
``TypedDict``. Moreover, not required keys should correspond to optional
function arguments, whereas required keys should correspond to required
function arguments. Again, the rest of the parameters have to be compatible.
Continuing the previous example::

    class Example(TypedDict):
        animal: Animal
        string: str
        number: NotRequired[int]

    def src(**kwargs: Unpack[Example]): ...
    def dest(*, animal: Dog, string: str, number: int = ...): ...

    dest = src  # OK!

It is worth pointing out that the destination function's parameters that are to
be compatible with the keys and values from the ``TypedDict`` must be keyword
only::

    def dest(dog: Dog, string: str, number: int = ...): ...

    dog: Dog = {"name": "Daisy", "breed": "labrador"}

    dest(dog, "some string")  # OK!

    dest = src                # Type checker error!
    dest(dog, "some string")  # The same call fails at
                              # runtime now because 'src' expects
                              # keyword arguments.

The reverse situation where the destination callable contains
``**kwargs: Unpack[TypedDict]`` and the source callable doesn't contain
``**kwargs`` should be disallowed. This is because, we cannot be sure that
additional keyword arguments are not being passed in when an instance of a
subclass had been assigned to a variable with a base class type and then
unpacked in the destination callable invocation::

    def dest(**kwargs: Unpack[Animal]): ...
    def src(name: str): ...

    dog: Dog = {"name": "Daisy", "breed": "Labrador"}
    animal: Animal = dog

    dest = src      # WRONG!
    dest(**animal)  # Fails at runtime.

Similar situation can happen even without inheritance as compatibility
between ``TypedDict``\s is based on structural subtyping.

Source contains untyped ``**kwargs``
""""""""""""""""""""""""""""""""""""

The destination callable contains ``**kwargs: Unpack[TypedDict]`` and the
source callable contains untyped ``**kwargs``::

    def src(**kwargs): ...
    def dest(**kwargs: Unpack[Movie]): ...

    dest = src  # OK!

Source contains traditionally typed ``**kwargs: T``
"""""""""""""""""""""""""""""""""""""""""""""""""""

The destination callable contains ``**kwargs: Unpack[TypedDict]``, the source
callable contains traditionally typed ``**kwargs: T`` and each of the
destination function ``TypedDict``'s fields is assignable to a variable of
type ``T``::

    class Vehicle:
        ...

    class Car(Vehicle):
        ...

    class Motorcycle(Vehicle):
        ...

    class Vehicles(TypedDict):
        car: Car
        moto: Motorcycle

    def dest(**kwargs: Unpack[Vehicles]): ...
    def src(**kwargs: Vehicle): ...

    dest = src  # OK!

On the other hand, if the destination callable contains either untyped or
traditionally typed ``**kwargs: T`` and the source callable is typed using
``**kwargs: Unpack[TypedDict]`` then an error should be generated, because
traditionally typed ``**kwargs`` aren't checked for keyword names.

To summarize, function parameters should behave contravariantly and function
return types should behave covariantly.

Passing kwargs inside a function to another function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`A previous point <PEP 692 assignment dest no kwargs>`_
mentions the problem of possibly passing additional keyword arguments by
assigning a subclass instance to a variable that has a base class type. Let's
consider the following example::

    class Animal(TypedDict):
        name: str

    class Dog(Animal):
        breed: str

    def takes_name(name: str): ...

    dog: Dog = {"name": "Daisy", "breed": "Labrador"}
    animal: Animal = dog

    def foo(**kwargs: Unpack[Animal]):
        print(kwargs["name"].capitalize())

    def bar(**kwargs: Unpack[Animal]):
        takes_name(**kwargs)

    def baz(animal: Animal):
        takes_name(**animal)

    def spam(**kwargs: Unpack[Animal]):
        baz(kwargs)

    foo(**animal)   # OK! foo only expects and uses keywords of 'Animal'.

    bar(**animal)   # WRONG! This will fail at runtime because 'breed' keyword
                    # will be passed to 'takes_name' as well.

    spam(**animal)  # WRONG! Again, 'breed' keyword will be eventually passed
                    # to 'takes_name'.

In the example above, the call to ``foo`` will not cause any issues at
runtime. Even though ``foo`` expects ``kwargs`` of type ``Animal`` it doesn't
matter if it receives additional arguments because it only reads and uses what
it needs completely ignoring any additional values.

The calls to ``bar`` and ``spam`` will fail because an unexpected keyword
argument will be passed to the ``takes_name`` function.

Therefore, ``kwargs`` hinted with an unpacked ``TypedDict`` can only be passed
to another function if the function to which unpacked kwargs are being passed
to has ``**kwargs`` in its signature as well, because then additional keywords
would not cause errors at runtime during function invocation. Otherwise, the
type checker should generate an error.

In cases similar to the ``bar`` function above the problem could be worked
around by explicitly dereferencing desired fields and using them as arguments
to perform the function call::

    def bar(**kwargs: Unpack[Animal]):
        name = kwargs["name"]
        takes_name(name)

Using ``Unpack`` with types other than ``TypedDict``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``TypedDict`` is the only permitted heterogeneous type for typing ``**kwargs``.
Therefore, in the context of typing ``**kwargs``, using ``Unpack`` with types
other than ``TypedDict`` should not be allowed and type checkers should
generate errors in such cases.

Callable
--------

Frameworks expecting callback functions of specific signatures might be
type hinted using ``Callable[[Arg1Type, Arg2Type], ReturnType]``.
Examples::

  from collections.abc import Callable

  def feeder(get_next_item: Callable[[], str]) -> None:
      # Body

  def async_query(on_success: Callable[[int], None],
                  on_error: Callable[[int, Exception], None]) -> None:
      # Body

It is possible to declare the return type of a callable without
specifying the call signature by substituting a literal ellipsis
(three dots) for the list of arguments::

  def partial(func: Callable[..., str], *args) -> Callable[..., str]:
      # Body

Note that there are no square brackets around the ellipsis.  The
arguments of the callback are completely unconstrained in this case
(and keyword arguments are acceptable).

Since using callbacks with keyword arguments is not perceived as a
common use case, there is currently no support for specifying keyword
arguments with ``Callable``.  Similarly, ``Callable`` does not support
specifying callback signatures with a variable number of arguments of a
specific type. For these use cases, see the section on
`Callback protocols`_.

Callback protocols
------------------

Protocols can be used to define flexible callback types that are hard
(or even impossible) to express using the ``Callable[...]`` syntax
specified by :pep:`484`, such as variadic, overloaded, and complex generic
callbacks. They can be defined as protocols with a ``__call__`` member::

  from typing import Protocol

  class Combiner(Protocol):
      def __call__(self, *vals: bytes,
                   maxlen: int | None = None) -> list[bytes]: ...

  def good_cb(*vals: bytes, maxlen: int | None = None) -> list[bytes]:
      ...
  def bad_cb(*vals: bytes, maxitems: int | None) -> list[bytes]:
      ...

  comb: Combiner = good_cb  # OK
  comb = bad_cb  # Error! Argument 2 has incompatible type because of
                 # different name and kind in the callback

Callback protocols and ``Callable[...]`` types can be used interchangeably.
