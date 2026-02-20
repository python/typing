.. _`type-forms`:

Type forms
==========

.. _`typeform`:

TypeForm
--------

(Originally specified in :pep:`747`.)

When a type expression is evaluated at runtime, the resulting value is a
*type form* object. This value encodes the information supplied in the type
expression, and it represents the type described by that type expression.

``TypeForm`` is a :term:`special form` that, when used in a type expression,
describes a set of type form objects. It accepts a single type argument, which
must be a :ref:`valid type expression <valid-type-expressions>`.
``TypeForm[T]`` describes the set of all type form objects that represent
the type ``T`` or types that are :term:`assignable` to ``T``. For example,
``TypeForm[str | None]`` describes the set of all type form objects that
represent a type assignable to ``str | None``::

  from typing import Any, Literal, Optional
  from typing_extensions import TypeForm

  ok1: TypeForm[str | None] = str | None  # OK
  ok2: TypeForm[str | None] = str  # OK
  ok3: TypeForm[str | None] = None  # OK
  ok4: TypeForm[str | None] = Literal[None]  # OK
  ok5: TypeForm[str | None] = Optional[str]  # OK
  ok6: TypeForm[str | None] = "str | None"  # OK
  ok7: TypeForm[str | None] = Any  # OK

  err1: TypeForm[str | None] = str | int  # Error
  err2: TypeForm[str | None] = list[str | None]  # Error

By this same definition, ``TypeForm[object]`` describes a type form object
that represents the type ``object`` or any type that is assignable to
``object``. Since all types in the Python type system are assignable to
``object``, ``TypeForm[object]`` describes the set of all type form objects
evaluated from all valid type expressions.

``TypeForm[Any]`` describes a ``TypeForm`` type whose type argument is not
statically known but is a valid type form object. It is assignable both
to and from any other ``TypeForm`` type (because ``Any`` is assignable both
to and from any type).

The type expression ``TypeForm``, with no type argument provided, is
equivalent to ``TypeForm[Any]``.

.. _`implicit-typeform-evaluation`:

Implicit ``TypeForm`` evaluation
--------------------------------

When a static type checker encounters a valid type expression, the evaluated
type of this expression should be assignable to ``TypeForm[T]`` if the type it
describes is assignable to ``T``.

For example, if a static type checker encounters the expression
``str | None``, it may normally evaluate its type as ``UnionType`` because it
produces a runtime value that is an instance of ``types.UnionType``. However,
because this expression is a valid type expression, it is also assignable to
the type ``TypeForm[str | None]``::

  from types import GenericAlias, UnionType
  from typing_extensions import TypeForm

  v1_actual: UnionType = str | None  # OK
  v1_type_form: TypeForm[str | None] = str | None  # OK

  v2_actual: GenericAlias = list[int]  # OK
  v2_type_form: TypeForm = list[int]  # OK

The ``Annotated`` special form is allowed in type expressions, so it can
also appear in an expression that is assignable to ``TypeForm``. Consistent
with the typing spec's rules for ``Annotated``, a static type checker may
choose to ignore any ``Annotated`` metadata that it does not understand::

  from typing import Annotated
  from typing_extensions import TypeForm

  v3: TypeForm[int | str] = Annotated[int | str, "metadata"]  # OK

A string literal expression containing a valid type expression should likewise
be assignable to ``TypeForm``::

  from typing_extensions import TypeForm

  v4: TypeForm[set[str]] = "set[str]"  # OK

.. _`valid-type-expressions`:

Valid type expressions
----------------------

The typing spec defines syntactic rules for type expressions in the form of a
:ref:`formal grammar <expression-grammar>`. Semantic rules are specified as
comments along with the grammar definition. Contextual requirements are
detailed throughout the typing spec in sections that discuss concepts that
appear within type expressions. For example, the special form ``Self`` can be
used in a type expression only within a class, and a type variable can be used
within a type expression only when it is associated with a valid scope.

A valid type expression is an expression that follows all of the syntactic,
semantic, and contextual rules for a type expression.

Expressions that are not valid type expressions should not evaluate to a
``TypeForm`` type::

  from typing import ClassVar, Final, Literal, Optional, Self, TypeVarTuple, Unpack
  from typing_extensions import TypeForm

  Ts = TypeVarTuple("Ts")
  var = 1

  bad1: TypeForm = tuple()  # Error: call expression not allowed in type expression
  bad2: TypeForm = (1, 2)  # Error: tuple expression not allowed in type expression
  bad3: TypeForm = 1  # Error: non-class object not allowed in type expression
  bad4: TypeForm = Self  # Error: Self not allowed outside of a class
  bad5: TypeForm = Literal[var]  # Error: variable not allowed in type expression
  bad6: TypeForm = Literal[f""]  # Error: f-strings not allowed in type expression
  bad7: TypeForm = ClassVar[int]  # Error: ClassVar not allowed in type expression
  bad8: TypeForm = Final[int]  # Error: Final not allowed in type expression
  bad9: TypeForm = Unpack[Ts]  # Error: Unpack not allowed in this context
  bad10: TypeForm = Optional  # Error: invalid use of Optional special form
  bad11: TypeForm = "int + str"  # Error: invalid quoted type expression

.. _`explicit-typeform-evaluation`:

Explicit ``TypeForm`` evaluation
--------------------------------

``TypeForm`` also acts as a function that can be called with a single
argument. Type checkers should validate that this argument is a valid type
expression::

  from typing import assert_type
  from typing_extensions import TypeForm

  x1 = TypeForm(str | None)
  assert_type(x1, TypeForm[str | None])

  x2 = TypeForm("list[int]")
  assert_type(x2, TypeForm[list[int]])

  x3 = TypeForm("type(1)")  # Error: invalid type expression

The static type of a ``TypeForm(T)`` expression is ``TypeForm[T]``.

At runtime the ``TypeForm(...)`` callable simply returns the value passed to
it.

This explicit syntax serves two purposes. First, it documents the developer's
intent to use the value as a type form object. Second, static type checkers
validate that all rules for type expressions are followed::

  x4 = type(1)  # No error, evaluates to "type[int]"

  x5 = TypeForm(type(1))  # Error: call not allowed in type expression

.. _`typeform-assignability`:

Assignability
-------------

``TypeForm`` has a single type parameter, which is covariant. That means
``TypeForm[B]`` is assignable to ``TypeForm[A]`` if ``B`` is assignable to
``A``::

  from typing_extensions import TypeForm

  def get_type_form() -> TypeForm[int]: ...

  t1: TypeForm[int | str] = get_type_form()  # OK
  t2: TypeForm[str] = get_type_form()  # Error

``type[T]`` is a subtype of ``TypeForm[T]``, which means that ``type[B]`` is
assignable to ``TypeForm[A]`` if ``B`` is assignable to ``A``::

  from typing_extensions import TypeForm

  def get_type() -> type[int]: ...

  t3: TypeForm[int | str] = get_type()  # OK
  t4: TypeForm[str] = get_type()  # Error

``TypeForm`` is a subtype of ``object`` and is assumed to have all of the
attributes and methods of ``object``.
