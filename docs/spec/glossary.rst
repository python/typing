.. _`glossary`:

Glossary
========

This section defines a few terms that may be used elsewhere in the specification.

The definition of "MAY", "MUST", and "SHOULD", and "SHOULD NOT" are
to be interpreted as described in :rfc:`2119`.

.. glossary::

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

   stub
      A file containing only type information, empty of runtime code
      (the filename ends in ``.pyi``). See :ref:`stub-files`.
