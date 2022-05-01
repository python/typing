.. _unreachable:

********************************************
Unreachable Code and Exhaustiveness Checking
********************************************

Sometimes it is necessary to write code that should never execute, and
sometimes we write code that we expect to execute, but that is actually
unreachable. The type checker can help in both cases.

In this guide, we'll cover:

- ``Never``, the primitive type used for unreachable code
- ``assert_never()``, a helper for exhaustiveness checking
- Directly marking code as unreachable
- Detecting unexpectedly unreachable code

``Never`` and ``NoReturn``
==========================

Type theory has a concept of a
`bottom type <https://en.wikipedia.org/wiki/Bottom_type>`__,
a type that has no values. Concretely, this can be used to represent
the return type of a function that never returns, or the argument type
of a function that may never be called. You can also think of the
bottom type as a union with no members.

The Python type system has long provided a type called ``NoReturn``.
While it was originally meant only for functions that never return,
this concept is naturally extended to the bottom type in general, and all
type checkers treat ``NoReturn`` as a general bottom type.

To make the meaning of this type more explicit, Python 3.11 and
typing-extensions 4.1 add a new primitive, ``Never``. To type checkers,
it has the same meaning as ``NoReturn``.

In this guide, we'll use ``Never`` for the bottom type, but if you cannot
use it yet, you can always use ``typing.NoReturn`` instead.

``assert_never()`` and Exhaustiveness Checking
==============================================

The ``Never`` type can be leveraged to perform static exhaustiveness checking,
where we use the type checker to make sure that we covered all possible
cases. For example, this can come up when code performs a separate action
for each member of an enum, or for each type in a union.

To have the type checker do exhaustiveness checking for us, we call a
function with a parameter typed as ``Never``. The type checker will allow
this call only if it can prove that the code is not reachable.

As an example, consider this simple calculator:

.. code:: python

   import enum
   from typing_extensions import Never

   def assert_never(arg: Never) -> Never:
       raise AssertionError("Expected code to be unreachable")

   class Op(enum.Enum):
       ADD = 1
       SUBTRACT = 2

   def calculate(left: int, op: Op, right: int) -> int:
       match op:
           case Op.ADD:
               return left + right
           case Op.SUBTRACT:
               return left - right
           case _:
               assert_never(op)

The ``match`` statement covers all members of the ``Op`` enum,
so the ``assert_never()`` call is unreachable and the type checker
will accept this code. However, if you add another member to the
enum (say, ``MULTIPLY``) but don't update the ``match`` statement,
the type checker will give an error saying that you are not handling
the ``MULTIPLY`` case.

Because the ``assert_never()`` helper function is frequently useful,
it is provided by the standard library as ``typing.assert_never``
starting in Python 3.11,
and is also present in ``typing_extensions`` starting at version 4.1.
However, it is also possible to define a similar function in your own
code, for example if you want to customize the runtime error message.

You can also use ``assert_never()`` with a sequence of ``if`` statements:

.. code:: python

   def calculate(left: int, op: Op, right: int) -> int:
       if op is Op.ADD:
           return left + right
       elif op is Op.SUBTRACT:
           return left - right
       else:
           assert_never(op)

Marking Code as Unreachable
===========================

Sometimes a piece of code is unreachable, but the type system is not
powerful enough to recognize that. For example, consider a function that
finds the lowest unused street number in a street:

.. code:: python

   import itertools

   def is_used(street: str, number: int) -> bool:
       ...
 
   def lowest_unused(street: str) -> int:
       for i in itertools.count(1):
           if not is_used(street, i):
               return i
       assert False, "unreachable"

Because ``itertools.count()`` is an infinite iterator, this function
will never reach the ``assert False`` statement. However, there is
no way for the type checker to know that, so without the ``assert False``,
the type checker will complain that the function is missing a return
statement.

Note how this is different from ``assert_never()``:

- If we used ``assert_never()`` in the ``lowest_unused()`` function,
  the type checker would produce an error, because the type checker
  cannot prove that the line is unreachable.
- If we used ``assert False`` instead of ``assert_never()`` in the
  ``calculate()`` example above, we would not get the benefits of
  exhaustiveness checking. If the code is actually reachable,
  the type checker will not warn us and we could hit the assertion
  at runtime.

While ``assert False`` is the most idiomatic way to express this pattern,
any statement that ends execution will do. For example, you could raise
an exception or call a function that returns ``Never``.

Detecting Unexpectedly Unreachable Code
=======================================

Another possible problem is code that is supposed to execute, but that
can actually be statically determined to be unreachable.
Some type checkers have an option that enables warnings for code
detected as unreachable (e.g., ``--warn-unreachable`` in mypy).
