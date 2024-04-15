Exceptions
==========

Some type checking behaviors, such as type narrowing and reachability analysis,
require a type checker to understand code flow. Code flow normally proceeds
from one statement to the next, but some statements such as ``for``, ``while``
and ``return`` can change the code flow. Similarly, ``try``/``except``/``finally``
statements affect code flow and therefore can affect type evaluation. For example::

    x = None
    try:
        some_function()
        x = 1
    except:
        pass

    # The type of `x` at this point could be None if `some_function` raises
    # an exception or `Literal[1]` if it doesn't, so a type checker may
    # choose to narrow its type based on this analysis.
    reveal_type(x)  # Literal[1] | None


Context Managers
----------------

Context managers may optionally "suppress" exceptions. When such a context
manager is used, any exceptions that are raised and otherwise uncaught within
the ``with`` block are caught by the context manager, and control continues
immediately after the ``with`` block. If a context manager does not suppress
exceptions (as is typically the case), any exceptions that are raised and
otherwise uncaught within the ``with`` block propagate beyond the ``with``
block.

Type checkers that employ code flow analysis must be able to distinguish
between these two cases. This is done by examining the return type
annotation of the ``__exit__`` method of the context manager.

If the return type of the ``__exit__`` method is specifically ``bool`` or
``Literal[True]``, a type checker should assume that exceptions *can be*
suppressed. For any other return type, a type checker should assume that
exceptions *are not* suppressed. Examples include: ``Any``, ``Literal[False]``,
``None``, and ``bool | None``.

This convention was chosen because most context managers do not suppress
exceptions, and it is common for their ``__exit__`` method to be annotated as
returning ``bool | None``. Context managers that suppress exceptions are
relatively rare, so they are considered a special case.

For example, the following context manager suppresses exceptions::

    class Suppress:
        def __enter__(self) -> None:
            pass

        def __exit__(self, exc_type, exc_value, traceback) -> bool:
            return True

    with Suppress():
        raise ValueError("This exception is suppressed")

    # The exception is suppressed, so this line is reachable.
    print("Code is reachable")
