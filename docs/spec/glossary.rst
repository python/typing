.. _`glossary`:

Glossary
========

This section defines a few terms that may be used elsewhere in the specification.

.. glossary::

   annotation expression
      An expression that is valid to use within an annotation. This is usually a
      :term:`type expression`, sometimes with additional :term:`type qualifiers <type qualifier>`.
      See :ref:`"Type and annotation expression" <annotation-expression>` for details.

   distribution
      The packaged file which is used to publish and distribute
      a release. (:pep:`426`)

   inline
      Inline type annotations are annotations that are included in the
      runtime code using :pep:`526` and
      :pep:`3107` syntax (the filename ends in ``.py``).

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

   type expression
      An expression that represents a type. The type system requires the use of type
      expressions within :term:`annotation expression` and also in several other contexts.
      See :ref:`"Type and annotation expression" <type-expression>` for details.

   type qualifier
      A type qualifier is a :term:`special form` that qualifies a :term:`type expression` to
      form an :term:`annotation expression`. For example, the type qualifier :ref:`Final <uppercase-final>`
      can be used around a type to indicate that the annotated value may not be overridden or modified.
      This term is also used for other special forms that modify a type, but using a different
      syntactic context, such as the `@final <at-final>` decorator.
