.. _`glossary`:

Glossary
========

This section defines a few terms that may be used elsewhere in the specification.

.. glossary::

   annotation expression
      An expression that is valid to use within an annotation. This is usually a
      :term:`type expression`, sometimes with additional :term:`type qualifiers <type qualifier>`.
      See :ref:`"Type and annotation expression" <annotation-expression>` for details.

   assignable
      If a type ``B`` is "assignable to" a type ``A``, a  type checker should
      not error on the assignment ``x: A = b``, where ``b`` is some expression
      whose type is ``B``. Similarly for function calls and returns: ``f(b)``
      where ``def f(x: A): ...`` and ``return b`` inside ``def f(...) -> A:``
      are both valid (not a type error) if and only if ``B`` is assignable to
      ``A``. In this case ``A`` is "assignable from" ``B``. For :term:`fully
      static types <fully static type>`, "assignable to" is equivalent to
      ":term:`subtype` of" and "assignable from" is equivalent to
      ":term:`supertype` of". For :term:`gradual types <gradual type>`, a type
      ``B`` is assignable to a type ``A`` if there exist :term:`fully static
      <fully static type>` :term:`materializations <materialize>` ``A'`` and
      ``B'`` of ``A`` and ``B``, respectively, such that ``B'`` is a
      :term:`subtype` of ``A'``. See :ref:`type-system-concepts`.

   consistent
      Two :term:`fully static types <fully static type>` are "consistent with"
      each other if they are the same type. Two gradual types are "consistent
      with" each other if they could :term:`materialize` to the same type. See
      :ref:`type-system-concepts`.

   consistent subtype
      "Consistent subtype" is synonymous with ":term:`assignable` to" (and
      "consistent supertype" is synonymous with ":term:`assignable` from"). See
      :ref:`type-system-concepts`.

   distribution
      The packaged file which is used to publish and distribute
      a release. (:pep:`426`)

   fully static type
      A type is "fully static" if it does not contain any :term:`gradual form`.
      Fully static types represent a set of possible runtime values. Fully
      static types participate in the :term:`subtype` relation. See
      :ref:`type-system-concepts`.

   gradual form
      A gradual form is a :term:`type expression` which makes the type it is
      part of not a :term:`fully static type`, but rather represent a set of
      possible static types. See :ref:`type-system-concepts`. The primary
      gradual form is :ref:`Any`. The ellipsis (`...`) is a gradual form in
      some, but not all, contexts. It is a gradual form when used in a
      :ref:`Callable` type, and when used in ``tuple[Any, ...]`` (but not in
      other :ref:`tuple <tuples>` types.)

   gradual type
      Types in the Python type system are "gradual types". A gradual type may
      be a :term:`fully static type`, or it may be :ref:`Any`, or a type that
      contains :ref:`Any` or another :term:`gradual form`. Unlike :term:`fully
      static types <fully static type>`, gradual types do not necessarily
      represent a single set of possible runtime values; instead they represent
      a set of possible static types. Gradual types do not participate in the
      :term:`subtype` relation, but they do participate in :term:`consistency
      <consistent>` and :term:`assignability <assignable>`. They can be
      :term:`materialized <materialize>` to a fully static type. See
      :ref:`type-system-concepts`.

   inline
      Inline type annotations are annotations that are included in the
      runtime code using :pep:`526` and
      :pep:`3107` syntax (the filename ends in ``.py``).

   materialize
      A :term:`gradual type` can be materialized to a more static type
      (possibly a :term:`fully static type`) by replacing :ref:`Any` with a
      type, or by replacing the `...` in a :ref:`Callable` type with a list of
      types, or by replacing ``tuple[Any, ...]`` with a specific-length tuple
      type. This materialization relation is key to defining
      :term:`assignability <assignable>` for gradual types. See
      :ref:`type-system-concepts`.

   module
      A file containing Python runtime code or stubbed type information.

   package
      A directory or directories that namespace Python modules.
      (Note the distinction between packages and :term:`distributions <distribution>`.
      While most distributions are named after the one package they install, some
      distributions install multiple packages.)

   special form
      A special form is an object that has a special meaning within the type system,
      comparable to a keyword in the language grammar. Examples include ``Any``,
      ``Generic``,  ``Literal``, and ``TypedDict``. Special forms can often but not always be used
      within :ref:`type expressions <type-expression>`. Special forms can usually
      be imported from the :py:mod:`typing` module or equivalently from ``typing_extensions``,
      but some special forms are placed in other modules.

   stub
      A file containing only type information, empty of runtime code
      (the filename ends in ``.pyi``). See :ref:`stub-files`.

   subtype
      A :term:`fully static type` ``B`` is a subtype of a :term:`fully static
      type` ``A`` if and only if the set of possible runtime values represented
      by ``B`` is a subset of the set of possible runtime values represented by
      ``A``. For nominal types (classes), subtyping is defined by inheritance.
      For structural types (see :ref:`Protocols`), subtyping is defined by a
      shared set of attributes and methods. Subtype is the inverse of
      :term:`supertype`. See :ref:`type-system-concepts`.

   supertype
      A :term:`fully static type` ``A`` is a supertype of a :term:`fully static
      type` ``B`` if and only if the set of possible runtime values represented
      by ``A`` is a superset of the set of possible runtime values represented
      by ``B``. Supertype is the inverse of :term:`subtype`. See
      :ref:`type-system-concepts`.

   type expression
      An expression that represents a type. The type system requires the use of type
      expressions within :term:`annotation expression` and also in several other contexts.
      See :ref:`"Type and annotation expression" <type-expression>` for details.

   type qualifier
      A type qualifier is a :term:`special form` that qualifies a :term:`type expression` to
      form an :term:`annotation expression`. For example, the type qualifier :ref:`Final <uppercase-final>`
      can be used around a type to indicate that the annotated value may not be overridden or modified.
      This term is also used for other special forms that modify a type, but using a different
      syntactic context, such as the :ref:`@final <at-final>` decorator.
