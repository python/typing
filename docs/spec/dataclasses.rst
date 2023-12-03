Dataclasses
===========

Type checkers should support dataclasses created through
the :py:mod:`dataclasses` module. In addition, the type system
contains a mechanism to make third-party classes behave like
standard dataclasses.

The ``dataclass_transform`` decorator
-------------------------------------

(Originally specified in :pep:`681`.)

Specification
^^^^^^^^^^^^^

This specification describes a decorator function in
the ``typing`` module named ``dataclass_transform``. This decorator
can be applied to either a function that is itself a decorator,
a class, or a metaclass. The presence of
``dataclass_transform`` tells a static type checker that the decorated
function, class, or metaclass performs runtime "magic" that transforms
a class, endowing it with dataclass-like behaviors.

If ``dataclass_transform`` is applied to a function, using the decorated
function as a decorator is assumed to apply dataclass-like semantics.
If the function has overloads, the ``dataclass_transform`` decorator can
be applied to the implementation of the function or any one, but not more
than one, of the overloads. When applied to an overload, the
``dataclass_transform`` decorator still impacts all usage of the
function.

If ``dataclass_transform`` is applied to a class, dataclass-like
semantics will be assumed for any class that directly or indirectly
derives from the decorated class or uses the decorated class as a
metaclass. Attributes on the decorated class and its base classes
are not considered to be fields.

Examples of each approach are shown in the following sections. Each
example creates a ``CustomerModel`` class with dataclass-like semantics.
The implementation of the decorated objects is omitted for brevity,
but we assume that they modify classes in the following ways:

* They synthesize an ``__init__`` method using data fields declared
  within the class and its parent classes.
* They synthesize ``__eq__`` and ``__ne__`` methods.

Type checkers will recognize that the
``CustomerModel`` class can be instantiated using the synthesized
``__init__`` method:

.. code-block:: python

  # Using positional arguments
  c1 = CustomerModel(327, "John Smith")

  # Using keyword arguments
  c2 = CustomerModel(id=327, name="John Smith")

  # These calls will generate runtime errors and should be flagged as
  # errors by a static type checker.
  c3 = CustomerModel()
  c4 = CustomerModel(327, first_name="John")
  c5 = CustomerModel(327, "John Smith", 0)

Decorator function example
""""""""""""""""""""""""""

.. code-block:: python

  _T = TypeVar("_T")

  # The ``create_model`` decorator is defined by a library.
  # This could be in a type stub or inline.
  @typing.dataclass_transform()
  def create_model(cls: Type[_T]) -> Type[_T]:
      cls.__init__ = ...
      cls.__eq__ = ...
      cls.__ne__ = ...
      return cls

  # The ``create_model`` decorator can now be used to create new model
  # classes, like this:
  @create_model
  class CustomerModel:
      id: int
      name: str

Class example
"""""""""""""

.. code-block:: python

  # The ``ModelBase`` class is defined by a library. This could be in
  # a type stub or inline.
  @typing.dataclass_transform()
  class ModelBase: ...

  # The ``ModelBase`` class can now be used to create new model
  # subclasses, like this:
  class CustomerModel(ModelBase):
      id: int
      name: str

Metaclass example
"""""""""""""""""

.. code-block:: python

  # The ``ModelMeta`` metaclass and ``ModelBase`` class are defined by
  # a library. This could be in a type stub or inline.
  @typing.dataclass_transform()
  class ModelMeta(type): ...

  class ModelBase(metaclass=ModelMeta): ...

  # The ``ModelBase`` class can now be used to create new model
  # subclasses, like this:
  class CustomerModel(ModelBase):
      id: int
      name: str

Decorator function and class/metaclass parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A decorator function, class, or metaclass that provides dataclass-like
functionality may accept parameters that modify certain behaviors.
This specification defines the following parameters that static type
checkers must honor if they are used by a dataclass transform. Each of
these parameters accepts a bool argument, and it must be possible for
the bool value (``True`` or ``False``) to be statically evaluated.

* ``eq``,  ``order``, ``frozen``, ``init`` and ``unsafe_hash`` are parameters
  supported in the stdlib dataclass, with meanings defined in
  :pep:`PEP 557 <557#id7>`.
* ``kw_only``, ``match_args`` and ``slots`` are parameters supported
  in the stdlib dataclass, first introduced in Python 3.10.

``dataclass_transform`` parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameters to ``dataclass_transform`` allow for some basic
customization of default behaviors:

.. code-block:: python

  _T = TypeVar("_T")

  def dataclass_transform(
      *,
      eq_default: bool = True,
      order_default: bool = False,
      kw_only_default: bool = False,
      frozen_default: bool = False,
      field_specifiers: tuple[type | Callable[..., Any], ...] = (),
      **kwargs: Any,
  ) -> Callable[[_T], _T]: ...

* ``eq_default`` indicates whether the ``eq`` parameter is assumed to
  be True or False if it is omitted by the caller. If not specified,
  ``eq_default`` will default to True (the default assumption for
  dataclass).
* ``order_default`` indicates whether the ``order`` parameter is
  assumed to be True or False if it is omitted by the caller. If not
  specified, ``order_default`` will default to False (the default
  assumption for dataclass).
* ``kw_only_default`` indicates whether the ``kw_only`` parameter is
  assumed to be True or False if it is omitted by the caller. If not
  specified, ``kw_only_default`` will default to False (the default
  assumption for dataclass).
* ``frozen_default`` indicates whether the ``frozen`` parameter is
  assumed to be True or False if it is omitted by the caller. If not
  specified, ``frozen_default`` will default to False (the default
  assumption for dataclass).
* ``field_specifiers`` specifies a static list of supported classes
  that describe fields. Some libraries also supply functions to
  allocate instances of field specifiers, and those functions may
  also be specified in this tuple. If not specified,
  ``field_specifiers`` will default to an empty tuple (no field
  specifiers supported). The standard dataclass behavior supports
  only one type of field specifier called ``Field`` plus a helper
  function (``field``) that instantiates this class, so if we were
  describing the stdlib dataclass behavior, we would provide the
  tuple argument ``(dataclasses.Field, dataclasses.field)``.
* ``kwargs`` allows arbitrary additional keyword args to be passed to
  ``dataclass_transform``. This gives type checkers the freedom to
  support experimental parameters without needing to wait for changes
  in ``typing.py``. Type checkers should report errors for any
  unrecognized parameters.

In the future, we may add additional parameters to
``dataclass_transform`` as needed to support common behaviors in user
code. These additions will be made after reaching consensus on
typing-sig rather than via additional PEPs.

The following sections provide additional examples showing how these
parameters are used.

Decorator function example
""""""""""""""""""""""""""

.. code-block:: python

  # Indicate that the ``create_model`` function assumes keyword-only
  # parameters for the synthesized ``__init__`` method unless it is
  # invoked with ``kw_only=False``. It always synthesizes order-related
  # methods and provides no way to override this behavior.
  @typing.dataclass_transform(kw_only_default=True, order_default=True)
  def create_model(
      *,
      frozen: bool = False,
      kw_only: bool = True,
  ) -> Callable[[Type[_T]], Type[_T]]: ...

  # Example of how this decorator would be used by code that imports
  # from this library:
  @create_model(frozen=True, kw_only=False)
  class CustomerModel:
      id: int
      name: str

Class example
"""""""""""""

.. code-block:: python

  # Indicate that classes that derive from this class default to
  # synthesizing comparison methods.
  @typing.dataclass_transform(eq_default=True, order_default=True)
  class ModelBase:
      def __init_subclass__(
          cls,
          *,
          init: bool = True,
          frozen: bool = False,
          eq: bool = True,
          order: bool = True,
      ):
          ...

  # Example of how this class would be used by code that imports
  # from this library:
  class CustomerModel(
      ModelBase,
      init=False,
      frozen=True,
      eq=False,
      order=False,
  ):
      id: int
      name: str

Metaclass example
"""""""""""""""""

.. code-block:: python

  # Indicate that classes that use this metaclass default to
  # synthesizing comparison methods.
  @typing.dataclass_transform(eq_default=True, order_default=True)
  class ModelMeta(type):
      def __new__(
          cls,
          name,
          bases,
          namespace,
          *,
          init: bool = True,
          frozen: bool = False,
          eq: bool = True,
          order: bool = True,
      ):
          ...

  class ModelBase(metaclass=ModelMeta):
      ...

  # Example of how this class would be used by code that imports
  # from this library:
  class CustomerModel(
      ModelBase,
      init=False,
      frozen=True,
      eq=False,
      order=False,
  ):
      id: int
      name: str


Field specifiers
^^^^^^^^^^^^^^^^^

Most libraries that support dataclass-like semantics provide one or
more "field specifier" types that allow a class definition to provide
additional metadata about each field in the class. This metadata can
describe, for example, default values, or indicate whether the field
should be included in the synthesized ``__init__`` method.

Field specifiers can be omitted in cases where additional metadata is
not required:

.. code-block:: python

  @dataclass
  class Employee:
      # Field with no specifier
      name: str

      # Field that uses field specifier class instance
      age: Optional[int] = field(default=None, init=False)

      # Field with type annotation and simple initializer to
      # describe default value
      is_paid_hourly: bool = True

      # Not a field (but rather a class variable) because type
      # annotation is not provided.
      office_number = "unassigned"


Field specifier parameters
""""""""""""""""""""""""""

Libraries that support dataclass-like semantics and support field
specifier classes typically use common parameter names to construct
these field specifiers. This specification formalizes the names and
meanings of the parameters that must be understood for static type
checkers. These standardized parameters must be keyword-only.

These parameters are a superset of those supported by
``dataclasses.field``, excluding those that do not have an impact on
type checking such as ``compare`` and ``hash``.

Field specifier classes are allowed to use other
parameters in their constructors, and those parameters can be
positional and may use other names.

* ``init`` is an optional bool parameter that indicates whether the
  field should be included in the synthesized ``__init__`` method. If
  unspecified, ``init`` defaults to True. Field specifier functions
  can use overloads that implicitly specify the value of ``init``
  using a literal bool value type
  (``Literal[False]`` or ``Literal[True]``).
* ``default`` is an optional parameter that provides the default value
  for the field.
* ``default_factory`` is an optional parameter that provides a runtime
  callback that returns the default value for the field. If neither
  ``default`` nor ``default_factory`` are specified, the field is
  assumed to have no default value and must be provided a value when
  the class is instantiated.
* ``factory`` is an alias for ``default_factory``. Stdlib dataclasses
  use the name ``default_factory``, but attrs uses the name ``factory``
  in many scenarios, so this alias is necessary for supporting attrs.
* ``kw_only`` is an optional bool parameter that indicates whether the
  field should be marked as keyword-only. If true, the field will be
  keyword-only. If false, it will not be keyword-only. If unspecified,
  the value of the ``kw_only`` parameter on the object decorated with
  ``dataclass_transform`` will be used, or if that is unspecified, the
  value of ``kw_only_default`` on ``dataclass_transform`` will be used.
* ``alias`` is an optional str parameter that provides an alternative
  name for the field. This alternative name is used in the synthesized
  ``__init__`` method.

It is an error to specify more than one of ``default``,
``default_factory`` and ``factory``.

This example demonstrates the above:

.. code-block:: python

  # Library code (within type stub or inline)
  # In this library, passing a resolver means that init must be False,
  # and the overload with Literal[False] enforces that.
  @overload
  def model_field(
          *,
          default: Optional[Any] = ...,
          resolver: Callable[[], Any],
          init: Literal[False] = False,
      ) -> Any: ...

  @overload
  def model_field(
          *,
          default: Optional[Any] = ...,
          resolver: None = None,
          init: bool = True,
      ) -> Any: ...

  @typing.dataclass_transform(
      kw_only_default=True,
      field_specifiers=(model_field, ))
  def create_model(
      *,
      init: bool = True,
  ) -> Callable[[Type[_T]], Type[_T]]: ...

  # Code that imports this library:
  @create_model(init=False)
  class CustomerModel:
      id: int = model_field(resolver=lambda : 0)
      name: str


Runtime behavior
^^^^^^^^^^^^^^^^

At runtime, the ``dataclass_transform`` decorator's only effect is to
set an attribute named ``__dataclass_transform__`` on the decorated
function or class to support introspection. The value of the attribute
should be a dict mapping the names of the ``dataclass_transform``
parameters to their values.

For example:

.. code-block:: python

  {
    "eq_default": True,
    "order_default": False,
    "kw_only_default": False,
    "field_specifiers": (),
    "kwargs": {}
  }


Dataclass semantics
^^^^^^^^^^^^^^^^^^^

Except where stated otherwise, classes impacted by
``dataclass_transform``, either by inheriting from a class that is
decorated with ``dataclass_transform`` or by being decorated with
a function decorated with ``dataclass_transform``, are assumed to
behave like stdlib ``dataclass``.

This includes, but is not limited to, the following semantics:

* Frozen dataclasses cannot inherit from non-frozen dataclasses. A
  class that has been decorated with ``dataclass_transform`` is
  considered neither frozen nor non-frozen, thus allowing frozen
  classes to inherit from it. Similarly, a class that directly
  specifies a metaclass that is decorated with ``dataclass_transform``
  is considered neither frozen nor non-frozen.

  Consider these class examples:

  .. code-block:: python

    # ModelBase is not considered either "frozen" or "non-frozen"
    # because it is decorated with ``dataclass_transform``
    @typing.dataclass_transform()
    class ModelBase(): ...

    # Vehicle is considered non-frozen because it does not specify
    # "frozen=True".
    class Vehicle(ModelBase):
        name: str

    # Car is a frozen class that derives from Vehicle, which is a
    # non-frozen class. This is an error.
    class Car(Vehicle, frozen=True):
        wheel_count: int

  And these similar metaclass examples:

  .. code-block:: python

    @typing.dataclass_transform()
    class ModelMeta(type): ...

    # ModelBase is not considered either "frozen" or "non-frozen"
    # because it directly specifies ModelMeta as its metaclass.
    class ModelBase(metaclass=ModelMeta): ...

    # Vehicle is considered non-frozen because it does not specify
    # "frozen=True".
    class Vehicle(ModelBase):
        name: str

    # Car is a frozen class that derives from Vehicle, which is a
    # non-frozen class. This is an error.
    class Car(Vehicle, frozen=True):
        wheel_count: int

* Field ordering and inheritance is assumed to follow the rules
  specified in :pep:`557 <557#inheritance>`. This includes the effects of
  overrides (redefining a field in a child class that has already been
  defined in a parent class).

* :pep:`PEP 557 indicates <557#post-init-parameters>` that
  all fields without default values must appear before
  fields with default values. Although not explicitly
  stated in PEP 557, this rule is ignored when ``init=False``, and
  this specification likewise ignores this requirement in that
  situation. Likewise, there is no need to enforce this ordering when
  keyword-only parameters are used for ``__init__``, so the rule is
  not enforced if ``kw_only`` semantics are in effect.

* As with ``dataclass``, method synthesis is skipped if it would
  overwrite a method that is explicitly declared within the class.
  Method declarations on base classes do not cause method synthesis to
  be skipped.

  For example, if a class declares an ``__init__`` method explicitly,
  an ``__init__`` method will not be synthesized for that class.

* KW_ONLY sentinel values are supported as described in `the Python
  docs <https://docs.python.org/3/library/dataclasses.html#dataclasses.KW_ONLY>`_
  and `bpo-43532 <https://bugs.python.org/issue43532>`_.

* ClassVar attributes are not considered dataclass fields and are
  `ignored by dataclass mechanisms <https://docs.python.org/3/library/dataclasses.html#class-variables>`_.


Undefined behavior
^^^^^^^^^^^^^^^^^^

If multiple ``dataclass_transform`` decorators are found, either on a
single function (including its overloads), a single class, or within a
class hierarchy, the resulting behavior is undefined. Library authors
should avoid these scenarios.
