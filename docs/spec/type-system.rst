The Python Type System
======================

This document describes a specification for the Python type system.

The type system aims to provide a standard syntax for type annotations,
opening up Python code to easier static analysis and refactoring,
potential runtime type checking, and (perhaps, in some contexts)
code generation utilizing type information.

Of these goals, static analysis is the most important.  This includes
support for off-line type checkers such as mypy, as well as providing
a standard notation that can be used by IDEs for code completion and
refactoring.

Purpose
-------

This specification aims to provide a full description of the Python
type system. For type checker authors, it provides a complete
description of expected semantics. For library authors, it provides
guarantees to rely on when working with multiple type checkers.

The type system was originally specified in a series of PEPs, starting
with :pep:`484`. This document is intended to replace those PEPs, and
was initially created by merging the specification sections of the
various PEPs. However, the PEPs are uneven in depth and do not fully
cover all aspects of the type system. Addressing these issues is an
ongoing project.

Non-goals
---------

While the typing module contains some building blocks for
runtime type checking -- in particular the ``get_type_hints()``
function -- third party packages would have to be developed to
implement specific runtime type checking functionality, for example
using decorators or metaclasses.  Using type hints for performance
optimizations is left as an exercise for the reader.

It should also be emphasized that **Python will remain a dynamically
typed language, and there is no desire to ever make type hints
mandatory, even by convention.**

Definition of terms
-------------------

This section defines a few terms that may be used elsewhere in the specification.

The definition of "MAY", "MUST", and "SHOULD", and "SHOULD NOT" are
to be interpreted as described in :rfc:`2119`.

"inline" - the types are part of the runtime code using :pep:`526` and
:pep:`3107` syntax (the filename ends in ``.py``).

"stubs" - files containing only type information, empty of runtime code
(the filename ends in ``.pyi``).

"Distributions" are the packaged files which are used to publish and distribute
a release. (:pep:`426`)

"Module" a file containing Python runtime code or stubbed type information.

"Package" a directory or directories that namespace Python modules.
(Note the distinction between packages and distributions.  While most
distributions are named after the one package they install, some
distributions install multiple packages.)
