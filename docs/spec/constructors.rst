Constructors
============

Calls to constructors require special handling within type checkers.

.. _`constructor-calls`:

Constructor Calls
-----------------

At runtime, a call to a class' constructor typically results in the invocation of
three methods in the following order:

#. The ``__call__`` method of the metaclass (which is typically supplied by the
   ``type`` class but can be overridden by a custom metaclass and which is
   responsible for calling the next two methods)
#. The ``__new__`` static method of the class
#. The ``__init__`` instance method of the class

Type checkers should mirror this runtime behavior when analyzing a constructor
call.

Metaclass ``__call__`` Method
-----------------------------

When evaluating a constructor call, a type checker should first check if the
class has a custom metaclass (a subclass of ``type``) that defines a ``__call__``
method. If so, it should evaluate the call of this method using the supplied
arguments. If the metaclass is ``type``, this step can be skipped.

If the evaluated return type of the ``__call__`` method indicates something
other than an instance of the class being constructed, a type checker should
assume that the metaclass ``__call__`` method is overriding ``type.__call__``
in some special manner, and it should not attempt to evaluate the ``__new__``
or ``__init__`` methods on the class. For example, some metaclass ``__call__``
methods are annotated to return ``NoReturn`` to indicate that constructor
calls are not supported for that class.

  ::

    class Meta(type):
        def __call__(cls, *args, **kwargs) -> NoReturn:
            raise TypeError("Cannot instantiate class")

    class MyClass(metaclass=Meta):
        def __new__(cls, *args, **kwargs) -> Self:
            return super().__new__(cls, *args, **kwargs)

    assert_type(MyClass(), Never)

If no return type annotation is provided for ``__call__``, a type checker may
assume that it does not override ``type.__call__`` in a special manner and
proceed as though the return type is an instance of the type specified by
the ``cls`` parameter.


``__new__`` Method
------------------

After the metaclass ``__call__`` method has been evaluated, a type checker
should evaluate the ``__new__`` method of the class (if applicable) using
the supplied arguments. This step should be skipped if the class does not
define a ``__new__`` method and does not inherit a ``__new__`` method from
a base class other than ``object``.

If the class is generic and explicitly specialized, the type checker should
partially specialize the ``__new__`` method using the supplied type arguments.
If the class is not explicitly specialized, class-scoped type variables should
be solved using the supplied arguments passed to the constructor call.

  ::

    class MyClass[T]:
        def __new__(cls, x: T) -> Self:
            return super().__new__(cls)

    # Constructor calls for specialized classes
    assert_type(MyClass[int](1), MyClass[int])
    assert_type(MyClass[float](1), MyClass[float])
    MyClass[int](1.0)  # Type error

    # Constructor calls for non-specialized classes
    assert_type(MyClass(1), MyClass[int])
    assert_type(MyClass(1.0), MyClass[float])

If any class-scoped type variables are not solved when evaluating the ``__new__``
method call using the supplied arguments, these type variables should be left
unsolved, allowing the ``__init__`` method (if applicable) to be used to solve
them.

  ::

      class MyClass[T]:
          def __new__(cls, *args, **kwargs) -> Self:
              return super().__new__(cls)

          def __init__(self, x: T) -> None:
              pass

      assert_type(MyClass(1), MyClass[int])
      assert_type(MyClass(""), MyClass[str])

For most classes, the return type for the ``__new__`` method is typically
``Self``, but other types are also allowed. For example, the ``__new__``
method may return an instance of a subclass or an instance of some completely
unrelated class.

If the evaluated return type of ``__new__`` is not the class being constructed
(or a subclass thereof), a type checker should assume that the ``__init__``
method will not be called. This is consistent with the runtime behavior of the
``type.__call__`` method. If the ``__new__`` method return type is a union with
one or more members that are not the class being constructed (or a subclass
thereof), a type checker should likewise assume that the ``__init__`` method
will not be called.

  ::

    class MyClass:
        def __new__(cls) -> int:
            return 0

        # In this case, the __init__ method should not be considered
        # by the type checker when evaluating a constructor call.
        def __init__(self, x: int):
            pass

    assert_type(MyClass(), int)

For purposes of this test, an explicit return type of ``Any`` (or a
union containing ``Any``) should be treated as a type that is not an instance
of the class being constructed.

  ::

    class MyClass:
        def __new__(cls) -> Any:
            return 0

        # The __init__ method will not be called in this case, so
        # it should not be evaluated.
        def __init__(self, x: int):
            pass

    assert_type(MyClass(), Any)

If the return type of ``__new__`` is not annotated, a type checker may assume
that the return type is ``Self`` and proceed with the assumption that the
``__init__`` method will be called.

If the class is generic, it is possible for a ``__new__`` method to override
the specialized class type and return a class instance that is specialized
with different type arguments.

  ::

    class MyClass[T]:
        def __new__(cls, *args, **kwargs) -> "MyClass[list[T]]":
            ...

    assert_type(MyClass[int](), MyClass[list[int]])

If the ``cls`` parameter within the ``__new__`` method is not annotated, type
checkers should infer a type of ``type[Self]``. Regardless of whether the
type of the ``cls`` parameter is explicit or inferred, the type checker should
bind the class being constructed to the ``cls`` parameter and report any type
errors that arise during binding.

  ::

    class MyClass[T]:
        def __new__(cls: "type[MyClass[int]]") -> "MyClass[int]": ...

    MyClass()  # OK
    MyClass[int]()  # OK
    MyClass[str]()  # Type Error


``__init__`` Method
-------------------

After evaluating the ``__new__`` method, a type checker should evaluate the
``__init__`` method (if applicable) using the supplied arguments. If the class
is generic and explicitly specialized (or specialized via the ``__new__`` method
return type), the type checker should partially specialize the ``__init__``
method using the supplied type arguments. If the class is not explicitly
specialized, class-scoped type variables should be solved using the supplied
arguments passed to the constructor call.

This step should be skipped if the class does not define an ``__init__`` method
and does not inherit an ``__init__`` method from a base class other than
``object``.

  ::

    class MyClass[T]:
        def __init__(self, x: T) -> None:
            ...

    # Constructor calls for specialized classes
    assert_type(MyClass[int](1), MyClass[int])
    assert_type(MyClass[float](1), MyClass[float])
    MyClass[int](1.0)  # Type error

    # Constructor calls for non-specialized classes
    assert_type(MyClass(1), MyClass[int])
    assert_type(MyClass(1.0), MyClass[float])

If the ``self`` parameter within the ``__init__`` method is not annotated, type
checkers should infer a type of ``Self``. Regardless of whether the ``self``
parameter type is explicit or inferred, a type checker should bind the class
being constructed to this parameter and report any type errors that arise
during binding.

  ::

    class MyClass[T]:
        def __init__(self: "MyClass[int]") -> None: ...

    MyClass()  # OK
    MyClass[int]()  # OK
    MyClass[str]()  # Type Error

The return type for ``__init__`` is always ``None``, which means the
method cannot influence the return type of the constructor call by specifying
a return type. There are cases where it is desirable for the ``__init__`` method
to influence the return type, especially when the ``__init__`` method is
overloaded. To enable this, type checkers should allow the ``self`` parameter
to be annotated with a type that influences the resulting type of the
constructor call.

  ::

    class MyClass1[T]:
        @overload
        def __init__(self: "MyClass1[list[int]]", value: int) -> None: ...
        @overload
        def __init__(self: "MyClass1[set[str]]", value: str) -> None: ...
        @overload
        def __init__(self, value: T) -> None: ...


    assert_type(MyClass1(0), MyClass1[list[int]])
    assert_type(MyClass1[int](3), MyClass1[int])
    assert_type(MyClass1(""), MyClass1[set[str]])
    assert_type(MyClass1(3.0), MyClass1[float])


Function-scoped type variables can also be used in the ``self``
annotation of an ``__init__`` method to influence the return type of the
constructor call.

  ::

    class MyClass2[T1, T2]:
        def __init__[V1, V2](self: "MyClass2[V1, V2]", value1: V1, value2: V2) -> None: ...

    assert_type(MyClass2(0, ""), MyClass2[int, str])
    assert_type(MyClass2[int, str](0, ""), MyClass2[int, str])

    class MyClass3[T1, T2]:
        def __init__[V1, V2](self: "MyClass3[V2, V1]", value1: V1, value2: V2) -> None: ...

    assert_type(MyClass3(0, ""), MyClass3[str, int])
    assert_type(MyClass3[str, int](0, ""), MyClass3[str, int])


Class-scoped type variables should not be used in the ``self`` annotation
because such use can lead to ambiguous or nonsensical type evaluation results.
Type checkers should report an error if a class-scoped type variable is used
within a type annotation for the ``self`` parameter in an ``__init__`` method.

  ::

    class MyClass4[T1, T2]:
        # The ``self`` annotation should result in a type error
        def __init__(self: "MyClass4[T2, T1]") -> None: ...


Classes Without ``__new__`` and ``__init__`` Methods
----------------------------------------------------

If a class does not define a ``__new__`` method or ``__init__`` method and
does not inherit either of these methods from a base class other than
``object``, a type checker should evaluate the argument list using the
``__new__`` and ``__init__`` methods from the ``object`` class.

  ::

    class MyClass5:
        pass

    MyClass5()  # OK
    MyClass5(1)  # Type error


Constructor Calls for type[T]
-----------------------------

When a value of type ``type[T]`` (where ``T`` is a concrete class or a type
variable) is called, a type checker should evaluate the constructor call as if
it is being made on the class ``T`` (or the class that represents the upper bound
of type variable ``T``). This means the type checker should use the ``__call__``
method of ``T``'s metaclass and the ``__new__`` and ``__init__`` methods of ``T``
to evaluate the constructor call.

It should be noted that such code could be unsafe because the type ``type[T]``
may represent subclasses of ``T``, and those subclasses could redefine the
``__new__`` and ``__init__`` methods in a way that is incompatible with the
base class. Likewise, the metaclass of ``T`` could redefine the ``__call__``
method in a way that is incompatible with the base metaclass.


Specialization During Construction
----------------------------------

As discussed above, if a class is generic and not explicitly specialized, its
type variables should be solved using the arguments passed to the ``__new__``
and ``__init__`` methods. If one or more type variables are not solved during
these method evaluations, they should take on their default values.

  ::

    from typing import Any, Self, assert_type

    class MyClass1[T1, T2]:
        def __new__(cls, x: T1) -> Self: ...

    assert_type(MyClass1(1), MyClass1[int, Any])

    class MyClass2[T1, T3 = str]:
        def __new__(cls, x: T1) -> Self: ...

    assert_type(MyClass2(1), MyClass2[int, str])


Consistency of ``__new__`` and ``__init__``
-------------------------------------------

Type checkers may optionally validate that the ``__new__`` and ``__init__``
methods for a class have :term:`consistent` signatures.

  ::

    class MyClass:
        def __new__(cls) -> Self:
            return super().__new__(cls)

        # Type error: __new__ and __init__ have inconsistent signatures
        def __init__(self, x: str) -> None:
            pass


Converting a Constructor to Callable
------------------------------------

Class objects are callable, which means the type of a class object can be
:term:`assignable` to a callable type.

  ::

    def accepts_callable[**P, R](cb: Callable[P, R]) -> Callable[P, R]:
        return cb

    class MyClass:
        def __init__(self, x: int) -> None:
            pass

    reveal_type(accepts_callable(MyClass))  # ``def (x: int) -> MyClass``

When converting a class to a callable type, a type checker should use the
following rules, which reflect the same rules specified above for evaluating
constructor calls:

1. If the class has a custom metaclass that defines a ``__call__`` method
   that is annotated with a return type other than a subclass of the
   class being constructed (or a union that contains such a type), a type
   checker should assume that the metaclass ``__call__`` method is overriding
   ``type.__call__`` in some special manner. In this case, the callable should
   be synthesized from the parameters and return type of the metaclass
   ``__call__`` method after it is bound to the class, and the ``__new__`` or
   ``__init__`` methods (if present) should be ignored. This is an uncommon
   case. In the more typical case where there is no custom metaclass that
   overrides ``type.__call__`` in a special manner, the metaclass ``__call__``
   signature should be ignored for purposes of converting to a callable type.
   If a custom metaclass ``__call__`` method is present but does not have an
   annotated return type, type checkers may assume that the method acts like
   ``type.__call__`` and proceed to the next step.

2. If the class defines a ``__new__`` method or inherits a ``__new__`` method
   from a base class other than ``object``, a type checker should synthesize a
   callable from the parameters and return type of that method after it is bound
   to the class.

3. If the return type of the method in step 2 evaluates to a type that is not a
   subclass of the class being constructed (or a union that includes such a
   class), the final callable type is based on the result of step 2, and the
   conversion process is complete. The ``__init__`` method is ignored in this
   case. This is consistent with the runtime behavior of the ``type.__call__``
   method.

4. If the class defines an ``__init__`` method or inherits an ``__init__`` method
   from a base class other than ``object``, a callable type should be synthesized
   from the parameters of the ``__init__`` method after it is bound to the class
   instance resulting from step 2. The return type of this synthesized callable
   should be the concrete value of ``Self``.

5. If step 2 and 4 both produce no result because the class does not define or
   inherit a ``__new__`` or ``__init__`` method from a class other than ``object``,
   the type checker should synthesize callable types from the ``__new__`` and
   ``__init__`` methods for the ``object`` class.

6. Steps 2, 4 and 5 will produce either one or two callable types. The final
   result of the conversion process is the union of these types. This will
   reflect the callable signatures of the applicable ``__new__`` and
   ``__init__`` methods.

  ::

    class A:
        """ No __new__ or __init__ """
        pass

    class B:
        """ __new__ and __init__ """
        def __new__(cls, *args, **kwargs) -> Self:
            ...

        def __init__(self, x: int) -> None:
            ...

    class C:
        """ __new__ but no __init__ """
        def __new__(cls, x: int) -> int:
            ...

    class CustomMeta(type):
        def __call__(cls) -> NoReturn:
            raise NotImplementedError("Class not constructable")

    class D(metaclass=CustomMeta):
        """ Custom metaclass that overrides type.__call__ """
        def __new__(cls, *args, **kwargs) -> Self:
            """ This __new__ is ignored for purposes of conversion """
            pass


    class E:
        """ __new__ that causes __init__ to be ignored """

        def __new__(cls) -> A:
            return A.__new__(cls)

        def __init__(self, x: int) -> None:
            """ This __init__ is ignored for purposes of conversion """
            ...


    reveal_type(accepts_callable(A))  # ``def () -> A``
    reveal_type(accepts_callable(B))  # ``def (*args, **kwargs) -> B | def (x: int) -> B``
    reveal_type(accepts_callable(C))  # ``def (x: int) -> int``
    reveal_type(accepts_callable(D))  # ``def () -> NoReturn``
    reveal_type(accepts_callable(E))  # ``def () -> A``


If the ``__init__`` or ``__new__`` method is overloaded, the callable
type should be synthesized from the overloads. The resulting callable type
itself will be overloaded.

  ::

    class MyClass:
        @overload
        def __init__(self, x: int) -> None: ...
        @overload
        def __init__(self, x: str) -> None: ...

    reveal_type(accepts_callable(MyClass))  # overload of ``def (x: int) -> MyClass`` and ``def (x: str) -> MyClass``


If the class is generic, the synthesized callable should include any class-scoped
type parameters that appear within the signature, but these type parameters should
be converted to function-scoped type parameters for the callable.
Any function-scoped type parameters in the ``__init__`` or ``__new__``
method should also be included as function-scoped type parameters in the synthesized
callable.

  ::

    class MyClass[T]:
        def __init__[V](self, x: T, y: list[V], z: V) -> None: ...

    reveal_type(accepts_callable(MyClass))  # ``def [T, V] (x: T, y: list[V], z: V) -> MyClass[T]``


Metaclass Constructors
----------------------

A class object is itself an instance of its :term:`python:metaclass`, so the
creation of a class is also a constructor call, one made on the metaclass. While
the sections above describe how a metaclass participates in the construction of
*instances* of a class, the following sections describe the construction of class objects
themselves.

A metaclass constructor is invoked in one of two ways:

1. Directly, by calling the metaclass with a class name, a tuple of base
   classes, and a namespace dictionary (for example,
   ``Meta(name, bases, namespace)``), optionally along with additional keyword
   arguments.
2. Implicitly, by a :keyword:`python:class` statement, which assembles these
   three arguments from the statement and the class body and then calls the metaclass.

In both cases, the metaclass call should be evaluated using the same rules
described in the sections above: the :meth:`!__call__` method of the metaclass's
own metaclass (typically :meth:`!type.__call__`) is invoked, which in turn calls
the :meth:`!__new__` and :meth:`!__init__` methods of the metaclass. These methods are
typically inherited from :class:`type`, whose type definitions require special
handling by type checkers, as described below.

The following example illustrates these rules applied to metaclass calls:

  ::

    class MetaMeta(type):
        def __call__(cls, *args, **kwargs) -> Never:
            raise TypeError("Classes cannot be created with this metaclass")

    class Meta1(type, metaclass=MetaMeta):
        pass

    # The __call__() method of the metaclass's own metaclass is evaluated first:
    assert_type(Meta1("A", (), {}), Never)

    class Meta2(type):
        def __new__(
            mcls,
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any],
            *,
            key: int,
        ):
            return super().__new__(mcls, name, bases, namespace)

    # Then, the __new__ and __init__ methods of the metaclass are evaluated:
    Meta2("B", (), {}, key=1)  # OK, evaluates to an instance of Meta2
    Meta2("B", (), {})  # Type error: missing argument "key"

    class Meta3(type):
        def __new__(
            mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
        ) -> int:
            return 0

        # Not evaluated, as __new__ does not return an instance of Meta3:
        def __init__(cls, x: str) -> None:
            pass

    assert_type(Meta3("C", (), {}), int)


The ``type`` Constructor
------------------------

In addition to being the default metaclass, :class:`type` serves a second purpose:
when called with a single argument, it returns the type of that argument rather than
creating a new class. :class:`type` therefore supports two distinct call forms,
which are distinguished by the number of positional arguments:

* ``type(obj, /)`` returns the class of ``obj``.
* ``type(name, bases, dict, /, **kwds)`` creates and returns a new class.

These two forms are typically declared as overloads of the :meth:`!__new__` and
:meth:`!__init__` methods in the type definition of :class:`type`. Both forms require
special-case handling by type checkers.

Although the single-argument form is typically declared with a return type of
``type``, type checkers should special-case this form and evaluate its result
as ``type[T]``, where ``T`` is the type of the argument.

  ::

    def func(x: int, y: int | str) -> None:
        assert_type(type(x), type[int])
        assert_type(type(y), type[int] | type[str])

At runtime, the single-argument form applies only when the class being called
is :class:`type` itself, and is not inherited by metaclasses: a single-argument call
to a subclass of :class:`type` raises a :exc:`TypeError`.

  ::

    class Meta(type):
        pass

    assert_type(type(1), type[int])  # OK, uses the single-argument form
    Meta(1)  # Type error: single-argument form does not apply to subclasses

    Meta("A", (), {})  # OK, uses the three-argument form

This special-casing applies only to the :meth:`!__new__` and :meth:`!__init__`
methods inherited from :class:`type`. If a metaclass defines its own :meth:`!__new__`
method that accepts a single argument, calls to it should be evaluated
using the rules for regular constructor calls described earlier in this
chapter.

The evaluated return type of the three-argument form is an instance of the
metaclass being called, consistent with the return type definition of
:meth:`!type.__new__`. Type checkers may infer a more precise type for the returned
class object, for example, one equivalent to a class defined by a :keyword:`class`
statement with the given name, base classes, and namespace.


Class Statements
----------------

When a :keyword:`class` statement is executed, the runtime performs the following
steps to create the new class object (see :ref:`python:metaclasses`):

1. The metaclass is determined. If a ``metaclass`` keyword argument is present
   in the class statement's argument list, it is used as a candidate;
   otherwise, :class:`type` is. The most derived metaclass among the candidate and
   the metaclasses of all base classes is selected. If no candidate is a
   (non-strict) subclass of all of the others, a :exc:`TypeError` is raised
   (see :ref:`py315:metaclass-determination`).
2. The class namespace is prepared. If the metaclass has a :attr:`!__prepare__`
   attribute, it is called as ``Meta.__prepare__(name, bases, **kwds)``, and
   its result is used as the namespace object.
3. The class body is executed within this namespace.
4. The metaclass is called as ``Meta(name, bases, namespace, **kwds)``, where
   ``kwds`` consists of the keyword arguments that appear in the class
   statement's argument list, excluding ``metaclass`` itself.

Type checkers may report an error for a class statement whose base classes
have incompatible metaclasses.

Type checkers should validate keyword arguments in a class statement's
argument list (other than ``metaclass``) by evaluating the implied metaclass
call using the constructor call rules described in :ref:`constructor-calls`.

  ::

    class Meta(type):
        def __new__(
            mcls,
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any],
            *,
            key: int,
        ):
            return super().__new__(mcls, name, bases, namespace)

    class MyClass1(metaclass=Meta, key=3):  # OK
        pass

    class MyClass2(metaclass=Meta, key=""):  # Type error: wrong type for "key"
        pass

    class MyClass3(metaclass=Meta):  # Type error: missing argument "key"
        pass

    Meta("MyClass4", (), {}, key=3)  # OK
    Meta("MyClass5", (), {}, key="")  # Type error: wrong type for "key"

Keyword arguments in a direct metaclass call (such as the last two calls in the
example above) require no special handling: they are validated as part of
evaluating the call using the standard constructor call rules.

Regardless of the evaluated return type of the implied metaclass call, a
:keyword:`class` statement defines a class, and type checkers should evaluate the
type of the bound name accordingly (``type[MyClass1]`` in the example above).
The implied metaclass call is evaluated only for the purpose of validating
its arguments.

Type checkers may validate the implied call to :attr:`!__prepare__`:

  ::

    class Meta(type):
        @classmethod
        def __prepare__(mcls, name: str, bases: tuple[type, ...]):  # No **kwds
            return {}

        def __new__(
            mcls,
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any],
            *,
            key: int,
        ):
            return super().__new__(mcls, name, bases, namespace)

    # The 'key' argument may result in a type checker error:
    class MyClass6(metaclass=Meta, key=3):
        pass

The ``metaclass`` argument can also be an arbitrary callable that is not a subclass
of :class:`type`. Support for this pattern is currently unspecified.


The ``__init_subclass__()`` Method
----------------------------------

:meth:`!type.__new__` invokes the :meth:`~object.__init_subclass__`
method of the parent class (the class that follows the newly created class in
its :term:`python:method resolution order`) passing the newly created class as
``cls`` along with the keyword arguments supplied to the metaclass constructor
(see :ref:`python:class-customization`).

:meth:`~object.__init_subclass__` is implicitly a class method: it is converted to
a :class:`classmethod` even when it is not explicitly decorated as one, and it is
not called for the class that defines it, only for its subclasses. Type checkers
should treat it as a classmethod if it isn't explicitly defined as one.

If the metaclass of the class being defined does not define its own
:meth:`!__new__` method (including when no explicit metaclass
is specified), type checkers should validate the keyword arguments in a
class statement's argument list against the :meth:`~object.__init_subclass__` method of
the parent class.

  ::

    class Base:
        def __init_subclass__(cls, *, flag: bool = False) -> None:
            super().__init_subclass__()

    class MyClass1(Base, flag=True):  # OK
        pass

    class MyClass2(Base, flag=""):  # Type error: wrong type for "flag"
        pass

    class MyClass3(Base, other=1):  # Type error: Base.__init_subclass__() got an unexpected keyword argument 'other'
        pass

    class MyClass4(other=1):  # Type error: MyClass4.__init_subclass__() takes no keyword arguments
        pass

A metaclass :meth:`!__init__` method has no effect on this rule: when the
metaclass does not define its own :meth:`!__new__` method, :meth:`!type.__new__`
still forwards the keyword arguments to :meth:`~object.__init_subclass__`, so
the keyword arguments should satisfy both the metaclass :meth:`!__init__`
method (as part of validating the implied metaclass call) and the
:meth:`~object.__init_subclass__` method of the parent class.

  ::

    class MetaInit(type):
        def __init__(
            cls,
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any],
            *,
            key: int,
        ) -> None:
            super().__init__(name, bases, namespace)

    # Type error: "key" is accepted by MetaInit.__init__(), but type.__new__()
    # forwards it to Base.__init_subclass__(), which does not accept it:
    class MyClass5(Base, metaclass=MetaInit, key=1):
        pass

The same forwarding occurs when the metaclass is called directly:
``type("D", (Base,), {}, flag=True)`` passes ``flag`` to
:meth:`!Base.__init_subclass__`. Type checkers may validate keyword
arguments in such calls against the :meth:`~object.__init_subclass__` method of
the parent class when the base classes can be statically determined.

If the metaclass defines its own :meth:`!__new__` method that accepts keyword
arguments only through a ``**kwargs`` parameter, whether these arguments are
forwarded to :meth:`!type.__new__` (and from there to
:meth:`~object.__init_subclass__`) cannot generally be determined statically.
In this situation, type checkers may additionally validate the keyword
arguments against the :meth:`~object.__init_subclass__` method of the parent
class.
