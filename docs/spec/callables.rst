.. _`callables`:

Callables
=========

Terminology
-----------

In this section, and throughout this specification, the term  "parameter"
refers to a named symbol associated with a function that receives the value of
an argument (or multiple arguments) passed to the function. The term
"argument" refers to a value passed to a function when it is called.

Python supports five kinds of parameters: positional-only, keyword-only,
standard (positional or keyword), variadic positional (``*args``), and
variadic keyword (``**kwargs``). Positional-only parameters can accept only
positional arguments, and keyword-only parameters can accept only keyword
arguments. Standard parameters can accept either positional or keyword
arguments. Parameters of the form ``*args`` and ``**kwargs`` are variadic
and accept zero or more positional or keyword arguments, respectively.

In the example below, ``a`` is a positional-only parameter, ``b`` is
a standard (positional or keyword) parameter, ``c`` is a keyword-only parameter,
``args`` is a variadic parameter that accepts additional positional arguments,
and ``kwargs`` is a variadic parameter that accepts additional keyword
arguments::

    def func(a: str, /, b, *args, c=0, **kwargs) -> None:
        ...

A function's "signature" refers to its list of parameters (including
the name, kind, optional declared type, and whether it has a default
argument value) plus its return type. The signature of the function above is
``(a: str, /, b, *args, c=..., **kwargs) -> None``. Note that the default
argument value for parameter ``c`` is denoted as ``...`` here because the
presence of a default value is considered part of the signature, but the
specific value is not.

The term "input signature" is used to refer to only the parameters of a function.
In the example above, the input signature is ``(a: str, /, b, *args, c=..., **kwargs)``.

Positional-only parameters
--------------------------

Within a function signature, positional-only parameters are separated from
non-positional-only parameters by a single forward slash ('/'). This
forward slash does not represent a parameter, but rather a delimiter. In this
example, ``a`` is a positional-only parameter and ``b`` is a standard
(positional or keyword) parameter::

    def func(a: int, /, b: int) -> None:
        ...

    func(1, 2)  # OK
    func(1, b=2)  # OK
    func(a=1, b=2)  # Error

Support for the ``/`` delimiter was introduced in Python 3.8 (:pep:`570`).
For compatibility with earlier versions of Python, the type system also
supports specifying positional-only parameters using a :ref:`double leading
underscore <pos-only-double-underscore>`.

Default argument values
-----------------------

In certain cases, it may be desirable to omit the default argument value for
a parameter. Examples include function definitions in stub files or methods
within a protocol or abstract base class. In such cases, the default value
may be given as an ellipsis. For example::

  def func(x: AnyStr, y: AnyStr = ...) -> AnyStr: ...

If a non-ellipsis default value is present and its type can be statically
evaluated, a type checker should verify that this type is :term:`assignable` to
the declared parameter's type::

    def func(x: int = 0): ...  # OK
    def func(x: int | None = None): ...  # OK
    def func(x: int = 0.0): ...  # Error
    def func(x: int = None): ...  # Error

.. _`annotating-args-kwargs`:

Annotating ``*args`` and ``**kwargs``
-------------------------------------

At runtime, the type of a variadic positional parameter (``*args``) is a
``tuple``, and the type of a variadic keyword parameter (``**kwargs``) is a
``dict``. However, when annotating these parameters, the type annotation
refers to the type of items within the ``tuple`` or ``dict`` (unless
``Unpack`` is used).

Therefore, the definition::

  def func(*args: str, **kwargs: int): ...

means that the function accepts an arbitrary number of positional arguments
of type ``str`` and an arbitrary number of keyword arguments of type ``int``.
For example, all of the following represent function calls with valid
arguments::

  func('a', 'b', 'c')
  func(x=1, y=2)
  func('', z=0)

In the body of function ``func``, the type of parameter ``args`` is
``tuple[str, ...]``, and the type of parameter ``kwargs`` is ``dict[str, int]``.

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


Function calls with standard dictionaries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Passing a dictionary of type ``dict[str, object]`` as a ``**kwargs`` argument
to a function that has ``**kwargs`` annotated with ``Unpack`` must generate a
type checker error. On the other hand, the behavior for functions using
standard, untyped dictionaries can depend on the type checker. For example::

    def func(**kwargs: Unpack[Movie]) -> None: ...

    movie: dict[str, object] = {"name": "Life of Brian", "year": 1979}
    func(**movie)  # WRONG! Movie is of type dict[str, object]

    typed_movie: Movie = {"name": "The Meaning of Life", "year": 1983}
    func(**typed_movie)  # OK!

    another_movie = {"name": "Life of Brian", "year": 1979}
    func(**another_movie)  # Depends on the type checker.

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

By default all keys in a ``TypedDict`` are required. This behavior can be
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

Assignments of a function typed with ``**kwargs: Unpack[Movie]`` and another
callable type should pass type checking only for the scenarios described below.

Source and destination contain ``**kwargs``
"""""""""""""""""""""""""""""""""""""""""""

Both destination and source functions have a ``**kwargs: Unpack[TypedDict]``
parameter and the destination function's ``TypedDict`` is :term:`assignable` to
the source function's ``TypedDict`` and the rest of the parameters are
assignable::

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
arguments are :term:`assignable` to the corresponding keys in source function's
``TypedDict``. Moreover, not required keys should correspond to optional
function arguments, whereas required keys should correspond to required
function arguments. Again, the rest of the parameters have to be assignable.
Continuing the previous example::

    class Example(TypedDict):
        animal: Animal
        string: str
        number: NotRequired[int]

    def src(**kwargs: Unpack[Example]): ...
    def dest(*, animal: Dog, string: str, number: int = ...): ...

    dest = src  # OK!

It is worth pointing out that the destination function's parameters that are to
be assignable to the keys and values from the ``TypedDict`` must be keyword
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

A similar situation can happen even without inheritance as :term:`assignability
<assignable>` between ``TypedDict``\s is :term:`structural`.

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
destination function ``TypedDict``'s fields is :term:`assignable` to a variable
of type ``T``::

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

:ref:`A previous point <PEP 692 assignment dest no kwargs>`
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

.. _`callable`:

Callable
--------

The ``Callable`` special form can be used to specify the signature of
a function within a type expression. The syntax is
``Callable[[Param1Type, Param2Type], ReturnType]``. For example::

    from collections.abc import Callable

    def func(cb: Callable[[int], str]) -> None:
        ...

    x: Callable[[], str]

Parameters specified using ``Callable`` are assumed to be positional-only.
The ``Callable`` form provides no way to specify keyword-only parameters,
variadic parameters, or default argument values. For these use cases, see
the section on `Callback protocols`_.

Meaning of ``...`` in ``Callable``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``Callable`` special form supports the use of ``...`` in place of the list
of parameter types. This is a :term:`gradual form` indicating that the type is
:term:`consistent` with any input signature::

    cb1: Callable[..., str]
    cb1 = lambda x: str(x)  # OK
    cb1 = lambda : ""  # OK

    cb2: Callable[[], str] = cb1  # OK

A ``...`` can also be used with ``Concatenate``. In this case, the parameters
prior to the ``...`` are required to be present in the input signature and
be assignable, but any additional parameters are permitted::

    cb3: Callable[Concatenate[int, ...], str]
    cb3 = lambda x: str(x)  # OK
    cb3 = lambda a, b, c: str(a)  # OK
    cb3 = lambda : ""  # Error
    cb3 = lambda *, a: str(a)  # Error


If the input signature in a function definition includes both a ``*args`` and
``**kwargs`` parameter and both are typed as ``Any`` (explicitly or implicitly
because it has no annotation), a type checker should treat this as the
equivalent of ``...``. Any other parameters in the signature are unaffected
and are retained as part of the signature::

    class Proto1(Protocol):
        def __call__(self, *args: Any, **kwargs: Any) -> None: ...

    class Proto2(Protocol):
        def __call__(self, a: int, /, *args, **kwargs) -> None: ...

    class Proto3(Protocol):
        def __call__(self, a: int, *args: Any, **kwargs: Any) -> None: ...

    class Proto4[**P](Protocol):
        def __call__(self, a: int, *args: P.args, **kwargs: P.kwargs) -> None: ...

    def func(p1: Proto1, p2: Proto2, p3: Proto3):
        assert_type(p1, Callable[..., None])  # OK
        assert_type(p2, Callable[Concatenate[int, ...], None])  # OK
        assert_type(p3, Callable[..., None])  # Error
        assert_type(p3, Proto4[...])  # OK

    class A:
        def method(self, a: int, /, *args: Any, k: str, **kwargs: Any) -> None:
            pass

    class B(A):
        # This override is OK because it is assignable to the parent's method.
        def method(self, a: float, /, b: int, *, k: str, m: str) -> None:
            pass


The ``...`` syntax can also be used to provide a :ref:`specialized value for a
ParamSpec <paramspec_valid_use_locations>` in a generic class or type alias.
For example::

    type Callback[**P] = Callable[P, str]

    def func(cb: Callable[[], str]) -> None:
        f: Callback[...] = cb  # OK

If ``...`` is used with signature concatenation, the ``...`` portion continues
to be :term:`consistent` with any input parameters::

    type CallbackWithInt[**P] = Callable[Concatenate[int, P], str]
    type CallbackWithStr[**P] = Callable[Concatenate[str, P], str]

    def func(cb: Callable[[int, str], str]) -> None:
        f1: Callable[Concatenate[int, ...], str] = cb # OK
        f2: Callable[Concatenate[str, ...], str] = cb # Error
        f3: CallbackWithInt[...] = cb  # OK
        f4: CallbackWithStr[...] = cb  # Error

.. _`callback-protocols`:

Callback protocols
------------------

Protocols can be used to define flexible callback types that are impossible to
express using the ``Callable`` special form as specified :ref:`above <callable>`.
This includes keyword parameters, variadic parameters, default argument values,
and overloads. They can be defined as protocols with a ``__call__`` member::

  from typing import Protocol

  class Combiner(Protocol):
      def __call__(self, *args: bytes, max_len: int | None = None) -> list[bytes]: ...

  def good_cb(*args: bytes, max_len: int | None = None) -> list[bytes]:
      ...
  def bad_cb(*args: bytes, max_items: int | None) -> list[bytes]:
      ...

  comb: Combiner = good_cb  # OK
  comb = bad_cb  # Error! Argument 2 is not assignable because of
                 # different parameter name and kind in the callback

Callback protocols and ``Callable[...]`` types can generally be used
interchangeably.


Assignability rules for callables
---------------------------------

A callable type ``B`` is :term:`assignable` to a callable type ``A`` if the
return type of ``B`` is assignable to the return type of ``A`` and the input
signature of ``B`` accepts all possible combinations of arguments that the
input signature of ``A`` accepts. All of the specific assignability rules
described below derive from this general rule.


Parameter types
^^^^^^^^^^^^^^^

Callable types are covariant with respect to their return types but
contravariant with respect to their parameter types. This means a callable
``B`` is :term:`assignable` to callable ``A`` if the types of the parameters of
``A`` are assignable to the parameters of ``B``. For example, ``(x: float) ->
int`` is assignable to ``(x: int) -> float``::

    def func(cb: Callable[[float], int]):
        f1: Callable[[int], float] = cb  # OK


Parameter kinds
^^^^^^^^^^^^^^^

Callable ``B`` is :term:`assignable` to callable ``A`` only if all keyword-only
parameters in ``A`` are present in ``B`` as either keyword-only parameters or
standard (positional or keyword) parameters. For example, ``(a: int) -> None``
is assignable to ``(*, a: int) -> None``, but the converse is not true. The
order of keyword-only parameters is ignored for purposes of assignability::

    class KwOnly(Protocol):
        def __call__(self, *, b: int, a: int) -> None: ...

    class Standard(Protocol):
        def __call__(self, a: int, b: int) -> None: ...

    def func(standard: Standard, kw_only: KwOnly):
        f1: KwOnly = standard  # OK
        f2: Standard = kw_only  # Error

Likewise, callable ``B`` is assignable to callable ``A`` only if all
positional-only parameters in ``A`` are present in ``B`` as either
positional-only parameters or standard (positional or keyword) parameters. The
names of positional-only parameters are ignored for purposes of assignability::

    class PosOnly(Protocol):
        def __call__(self, not_a: int, /) -> None: ...

    class Standard(Protocol):
        def __call__(self, a: int) -> None: ...

    def func(standard: Standard, pos_only: PosOnly):
        f1: PosOnly = standard  # OK
        f2: Standard = pos_only  # Error


``*args`` parameters
^^^^^^^^^^^^^^^^^^^^

If a callable ``A`` has a signature with a ``*args`` parameter, callable ``B``
must also have a ``*args`` parameter to be :term:`assignable` to ``A``, and the
type of ``A``'s ``*args`` parameter must be assignable to ``B``'s ``*args``
parameter::

    class NoArgs(Protocol):
        def __call__(self) -> None: ...

    class IntArgs(Protocol):
        def __call__(self, *args: int) -> None: ...

    class FloatArgs(Protocol):
        def __call__(self, *args: float) -> None: ...

    def func(no_args: NoArgs, int_args: IntArgs, float_args: FloatArgs):
        f1: NoArgs = int_args  # OK
        f2: NoArgs = float_args  # OK

        f3: IntArgs = no_args  # Error: missing *args parameter
        f4: IntArgs = float_args  # OK

        f5: FloatArgs = no_args  # Error: missing *args parameter
        f6: FloatArgs = int_args  # Error: float is not assignable to int

If a callable ``A`` has a signature with one or more positional-only
parameters, a callable ``B`` is assignable to ``A`` only if ``B`` has an
``*args`` parameter whose type is assignable from the types of any
otherwise-unmatched positional-only parameters in ``A``::

    class PosOnly(Protocol):
        def __call__(self, a: int, b: str, /) -> None: ...

    class IntArgs(Protocol):
        def __call__(self, *args: int) -> None: ...

    class IntStrArgs(Protocol):
        def __call__(self, *args: int | str) -> None: ...

    class StrArgs(Protocol):
        def __call__(self, a: int, /, *args: str) -> None: ...

    class Standard(Protocol):
        def __call__(self, a: int, b: str) -> None: ...

    def func(int_args: IntArgs, int_str_args: IntStrArgs, str_args: StrArgs):
        f1: PosOnly = int_args  # Error: str is not assignable to int
        f2: PosOnly = int_str_args  # OK
        f3: PosOnly = str_args  # OK
        f4: IntStrArgs = str_args  # Error: int | str is not assignable to str
        f5: IntStrArgs = int_args  # Error: int | str is not assignable to int
        f6: StrArgs = int_str_args  # OK
        f7: StrArgs = int_args  # Error: str is not assignable to int
        f8: IntArgs = int_str_args  # OK
        f9: IntArgs = str_args  # Error: int is not assignable to str
        f10: Standard = int_str_args  # Error: keyword parameters a and b missing
        f11: Standard = str_args  # Error: keyword parameter b missing


``**kwargs`` parameters
^^^^^^^^^^^^^^^^^^^^^^^

If a callable ``A`` has a signature with a ``**kwargs`` parameter (without an
unpacked ``TypedDict`` type annotation), callable ``B`` must also have a
``**kwargs`` parameter to be :term:`assignable` to ``A``, and the type of
``A``'s ``**kwargs`` parameter must be assignable to ``B``'s ``**kwargs``
parameter::

    class NoKwargs(Protocol):
        def __call__(self) -> None: ...

    class IntKwargs(Protocol):
        def __call__(self, **kwargs: int) -> None: ...

    class FloatKwargs(Protocol):
        def __call__(self, **kwargs: float) -> None: ...

    def func(no_kwargs: NoKwargs, int_kwargs: IntKwargs, float_kwargs: FloatKwargs):
        f1: NoKwargs = int_kwargs  # OK
        f2: NoKwargs = float_kwargs  # OK

        f3: IntKwargs = no_kwargs  # Error: missing **kwargs parameter
        f4: IntKwargs = float_kwargs  # OK

        f5: FloatKwargs = no_kwargs  # Error: missing **kwargs parameter
        f6: FloatKwargs = int_kwargs  # Error: float is not assignable to int

If a callable ``A`` has a signature with one or more keyword-only parameters,
a callable ``B`` is assignable to ``A`` if ``B`` has a ``**kwargs`` parameter
whose type is assignable from the types of any otherwise-unmatched keyword-only
parameters in ``A``::

    class KwOnly(Protocol):
        def __call__(self, *, a: int, b: str) -> None: ...

    class IntKwargs(Protocol):
        def __call__(self, **kwargs: int) -> None: ...

    class IntStrKwargs(Protocol):
        def __call__(self, **kwargs: int | str) -> None: ...

    class StrKwargs(Protocol):
        def __call__(self, *, a: int, **kwargs: str) -> None: ...

    class Standard(Protocol):
        def __call__(self, a: int, b: str) -> None: ...

    def func(int_kwargs: IntKwargs, int_str_kwargs: IntStrKwargs, str_kwargs: StrKwargs):
        f1: KwOnly = int_kwargs  # Error: str is not assignable to int
        f2: KwOnly = int_str_kwargs  # OK
        f3: KwOnly = str_kwargs  # OK
        f4: IntStrKwargs = str_kwargs  # Error: int | str is not assignable to str
        f5: IntStrKwargs = int_kwargs  # Error: int | str is not assignable to int
        f6: StrKwargs = int_str_kwargs  # OK
        f7: StrKwargs = int_kwargs  # Error: str is not assignable to int
        f8: IntKwargs = int_str_kwargs  # OK
        f9: IntKwargs = str_kwargs  # Error: int is not assignable to str
        f10: Standard = int_str_kwargs  # Error: Does not accept positional arguments
        f11: Standard = str_kwargs  # Error: Does not accept positional arguments

Assignability relationships for callable signatures that contain a ``**kwargs``
with an unpacked ``TypedDict`` are described in the section :ref:`above <unpack-kwargs>`.


Signatures with ParamSpecs
^^^^^^^^^^^^^^^^^^^^^^^^^^

A signature that includes ``*args: P.args, **kwargs: P.kwargs`` is equivalent
to a ``Callable`` parameterized by ``P``::

    class ProtocolWithP[**P](Protocol):
        def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None: ...

    type TypeAliasWithP[**P] = Callable[P, None]

    def func[**P](proto: ProtocolWithP[P], ta: TypeAliasWithP[P]):
        # These two types are equivalent
        f1: TypeAliasWithP[P] = proto  # OK
        f2: ProtocolWithP[P] = ta  # OK


Default argument values
^^^^^^^^^^^^^^^^^^^^^^^

If a callable ``C`` has a parameter ``x`` with a default argument value and
``A`` is the same as ``C`` except that ``x`` has no default argument, then
``C`` is :term:`assignable` to ``A``. ``C`` is also assignable to ``A`` if
``A`` is the same as ``C`` with parameter ``x`` removed::

    class DefaultArg(Protocol):
        def __call__(self, x: int = 0) -> None: ...

    class NoDefaultArg(Protocol):
        def __call__(self, x: int) -> None: ...

    class NoX(Protocol):
        def __call__(self) -> None: ...

    def func(default_arg: DefaultArg):
        f1: NoDefaultArg = default_arg  # OK
        f2: NoX = default_arg  # OK


Overloads
^^^^^^^^^

If a callable ``B`` is overloaded with two or more signatures, it is
:term:`assignable` to callable ``A`` if *at least one* of the overloaded
signatures in ``B`` is assignable to ``A``::

    class Overloaded(Protocol):
        @overload
        def __call__(self, x: int) -> int: ...
        @overload
        def __call__(self, x: str) -> str: ...

    class IntArg(Protocol):
        def __call__(self, x: int) -> int: ...

    class StrArg(Protocol):
        def __call__(self, x: str) -> str: ...

    class FloatArg(Protocol):
        def __call__(self, x: float) -> float: ...

    def func(overloaded: Overloaded):
        f1: IntArg = overloaded  # OK
        f2: StrArg = overloaded  # OK
        f3: FloatArg = overloaded  # Error

If a callable ``A`` is overloaded with two or more signatures, callable ``B``
is assignable to ``A`` if ``B`` is assignable to *all* of the signatures in
``A``::

    class Overloaded(Protocol):
        @overload
        def __call__(self, x: int, y: str) -> float: ...
        @overload
        def __call__(self, x: str) -> complex: ...

    class StrArg(Protocol):
        def __call__(self, x: str) -> complex: ...

    class IntStrArg(Protocol):
        def __call__(self, x: int | str, y: str = "") -> int: ...

    def func(int_str_arg: IntStrArg, str_arg: StrArg):
        f1: Overloaded = int_str_arg  # OK
        f2: Overloaded = str_arg  # Error
