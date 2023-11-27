.. _typing-anti-pitch:

Reasons to avoid static type checking
=====================================

In the words of :pep:`484`:

    It should also be emphasized that Python will remain a dynamically typed language, and
    the authors have no desire to ever make type hints mandatory, even by convention.

The idea that dynamism in Python is a strength of the language is reflected in the fact that
Python's type system is gradual. See :pep:`483` for details, but the long and short of this is
that you can add static types to your codebase only to the extent that you want to, and static
type checkers and other tools should be able to put up with this.

It's also worth noting that "static type checking" encompasses a spectrum of possible degrees of
strictness. On the one hand, you can set yourself up so that your type checker does almost nothing.
On the other -- well, I love type checking, but I would quit Python if I had to enable all
possible strictness checks that type checkers offer.

Anyway, with all that said, here's a list of possible reasons to not use static type checking
in Python:

* You simply don't want to. Python is a tool that is meant to serve you. Python is a big tent,
  multi-paradigm language that generally allows you to do things in the way that best suits your
  needs, as best determined by you.

* Type annotations can both help and hurt readability. While type annotations can serve both
  humans and machines, particularly complex annotations or changes to idioms serve machines more
  than they do humans. Readability counts.

* The cost-benefit ratio isn't good enough. Pleasing static type checkers requires a non-zero amount
  of busy work. If this isn't worth the extra confidence you get, you shouldn't add static type
  checking.

* Your codebase fits in your developers' heads. Opinions vary, but people tend to agree that at
  some number of developers and lines of code, static type checking confers significantly more
  benefit. You don't feel like you're there yet.

* If you maintain high test coverage, that might provide sufficient quality assurance for your
  needs (acknowledging that static type checking and tests enforce different things; static type
  checking usually cannot validate logic, tests can often not prove invariants of your code to
  hold).

* Your codebase is old, large and has been working fine without static type checking for years.
  While Python's type system is designed to
  `allow gradual adoption of static type checking <https://mypy.readthedocs.io/en/stable/existing_code.html>`_,
  the total cost of adding type annotations to a large extant codebase can be prohibitive.

* Your application uses a particularly dynamic framework or your library does enough dynamic things
  that type checking would be unlikely to help your developers and users. Migrating application
  frameworks could be costly. Either a) redesigning your library in ways that static type checkers
  could better understand or b) figuring out clever type annotations to twist the arms of type
  checkers would take a lot of effort.

* Your codebase has suffered at the hands of `Hyrum's Law <https://www.hyrumslaw.com/>`_
  and all possible observable behaviour is depended on. In order to avoid false positives for your
  users, all your types end up being either a) complicated ``Protocol``\s that are hard to maintain,
  or b) ``Any`` in which case there's not much point. (On the other hand, static type checking could
  be a good solution for communicating to users what behaviour they should be allowed to rely on)

* You're not opposed to type checking in theory, but you dislike Python type checkers in practice.
  Maybe they don't understand enough of the idioms you use, maybe you'd like them to infer more
  instead of relying on explicit annotations, maybe they're too slow, maybe they don't integrate
  well with your editor, maybe they're too hard to configure. Whatever the reason -- it just doesn't
  work for your project.

* Type checking in Python isn't actually strict enough, powerful enough or expressive enough for
  you. Python type checkers end up making various decisions out of pragmatism, or due to limited
  resources, and these decisions might not be the ones for you. This might mean that typed Python
  simply isn't the right language for you, or you need to find other methods to enforce the
  properties you desire.

Advice for maintainers of untyped libraries
*******************************************

You've made the decision that adding static types isn't the right choice for your library. But
perhaps you'd still like to help your users who do use static type checking -- and maybe you have
some enthusiastic would-be contributors willing to help with this.

One option is encourage such contributors to publish a :pep:`561` stub-only package that is
maintained separately from your main project. They could also contribute these stubs to the
`typeshed <https://github.com/python/typeshed>`_ project.

Note that if you're willing to maintain the stubs, but you don't wish to have them inline and don't
want to statically type check your code, you can accomplish this by distributing type stubs inside
your package. See :ref:`libraries` for more information. See :ref:`writing_stubs` for advice on
how to help maintain type stubs.

If more users pester you about adding static types, feel free to link them to this document. And if
you ever change your mind, make sure to check out some of the other guides in this documentation,
and ask any questions you have over at `Python's typing discussions <https://github.com/python/typing/discussions>`_.
