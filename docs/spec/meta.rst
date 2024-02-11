.. _`spec-meta`:

Meta-topics
===========

About this specification
------------------------

This document was created following the acceptance of :pep:`729`
to serve as a specification for the Python type system. The
initial text consists of the "Specification" sections of :pep:`484`
and subsequent typing-related PEPs, pasted together and reorganized.
This creates a document that encompasses all aspects of the type
system that have been specified in PEPs, but not necessarily a
coherent whole. The hope is that incremental improvements will
be made to this document to make it more coherent and complete.

Changing the specification
--------------------------

Changes to the specification come in three kinds:

- Minor, non-substantive changes can simply be proposed as PRs to
  the `python/typing <https://github.com/python/typing>`__ repository,
  and may be merged by anyone with commit access. Such changes may
  include formatting fixes, linking improvements, etc.
- Substantive changes that do not rise to the level of a PEP must
  be approved by the Typing Council. The procedure is described below.
- Major changes should go through the PEP process, as described in
  :pep:`1`. What counts as a major change is not precisely defined,
  but it would generally include any change of a similar magnitude
  to `previous typing PEPs <https://peps.python.org/topic/typing/>`__.

Changes that need Typing Council approval go through three steps:

- Open a discussion on `discuss.python.org <https://discuss.python.org/c/typing/32>`__
  describing the issue.
- Open a PR on `python/typing <https://github.com/python/typing>`__
  that changes the spec and, if applicable, the
  `conformance test suite <https://github.com/python/typing/tree/main/conformance>`__.
- `Open an issue <https://github.com/python/typing-council/issues/new>`__ on
  the Typing Council's issue tracker asking for a decision.

The Typing Council has `published <https://github.com/python/typing-council/blob/main/README.md>`__
some guidance on useful information to gather when proposing a change
to the spec, including:

- A survey of the current behavior of major type checkers.
- A rationale for why the proposed behavior is better than alternatives.
- An implementation or proposed implementation of the proposed behavior
  in at least one major type checker.
