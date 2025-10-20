*****************************************
The Trouble (Or Lack Thereof) With Lambda
*****************************************

:ref:`Lambda` expressions are a common and useful part of the Python programming language.
However, there is one problem with them: syntactically, they do not allow for type
annotations. While it is perfectly simple to write ``lambda x: x``, you cannot directly
indicate a type for x. (Type annotations are indicated by a colon, and so is the end
of the lambda parameter list. Where would the type annotation go?)

However, despite this infelicity, lambda expressions are not immune from static typing,
and in fact follow the same static type rules as everything else. Type checkers try
to deduce the type of the lambda arguments and return value, and if they can't they
fall back to ``Any``. Due to the inability to directly indicate types for these,
``Any`` tends to pop up quite often here. This means that many type errors may occur
here unnoticed, which is bad. For instance, the following example is a runtime type
error, but is uncaught in most (perhaps all) type checkers:

.. code-block:: python

   f1 = lambda a, b: a * b
   f1(1, "a")

(The alternative way of writing this, ``(lambda a, b: a + b)(1, "a")``, is typically
caught by type checkers, because it is simple and immediate enough that they are able
to deduce that a type error will occur.)

There are some workarounds to this problem, which all involve assigning the lambda to
something, in one way or another, and annotating that. This is a bit unfortunate,
because the idiomatic use of a lambda involves not doing that. In fact, at that point
you might as well just define a normal function. Let's call that our first workaround.

``def f(x: object) -> object: return x``

The second workaround is equivalent: assigning the lambda to a variable, and annotating
the type of that variable with a :ref:`Callable`

``f: Callable[[object], object] lambda x: x``

:ref:`Type comments on function definitions` do not actually work on lambda, nor do
normal :ref:`Type comments` help (although you can use a type commment on an assignment
to a variable with a lambda, of course; however this will have to be the Callable
syntax and not the function-arrow special one).

Most type checkers include an option to emit a warning if they aren't able to deduce
the type of an expression; this should be helpful if you want to avoid silent uncaught
type errors resulting from lambda expressions being deduced as ``Any``.

In conclusion:

1. There is no way to explicitly annotation lambda arguments or return values in the
lmabdas themselves.

2. However, static typing rules still apply to lambdas, including type deduction.

3. Many lambdas get deduced as ``Any``, which might suppress the reporting of other
type errors.

4. However, many lambdas get deduced fine, and for those it's not a problem.

5. If you want to annotate the type of lambdas, you can bind them and annotate them
there.

6. Most type checkers have a setting that will warn you if anything gets deduced as
``Any``, and you can use that to avoid false negatives relating to lambda.
