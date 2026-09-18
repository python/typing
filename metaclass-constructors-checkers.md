# Metaclass constructors: spec examples vs. type checkers

This document runs the examples from the [Metaclass Constructors](docs/spec/constructors.rst)
spec sections against CPython and four type checkers, to assess how far current
implementations are from the proposed behavior.

Environment:

- Runtime: CPython 3.14.5
- mypy 2.3.0 (default settings)
- pyright 1.1.411 (default settings)
- ty 0.0.65 (default settings)
- pyrefly 1.1.1 (`--preset default`; the implicit `basic` preset disables
  call-shape validation entirely and reports nothing on these examples)

Each significant line is annotated with a comment of the form:

```
# spec: <expected> | runtime: <ok or exception> | mypy: <ok/error> | pyright: <ok/error> | ty: <ok/error> | pyrefly: <ok/error>
```

- `spec:` is what the spec expects a type checker to report: `error` (should),
  `may error` (optional), or `ok` (no error). For `assert_type()` lines, `ok`
  means the assertion should pass.
- `runtime:` is what CPython does when the statement is executed. Note that a
  line can be a type error while running fine (e.g. a wrongly typed keyword
  value is not checked at runtime), and vice versa (an `assert_type()` whose
  argument raises).
- A checker column says `error` if the checker reports any diagnostic on that
  line, `ok` otherwise.

## Metaclass Constructors (intro example)

```python
from typing import Any, Never, assert_type


class MetaMeta(type):
    def __call__(cls, *args, **kwargs) -> Never:
        raise TypeError("Classes cannot be created with this metaclass")


class Meta1(type, metaclass=MetaMeta):
    pass


# spec: ok | runtime: TypeError (by design) | mypy: error | pyright: ok | ty: ok | pyrefly: ok
assert_type(Meta1("A", (), {}), Never)


class Meta2(type):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        key: int,
    ):
        return super().__new__(mcls, name, bases, namespace)


# spec: ok | runtime: ok | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
Meta2("B", (), {}, key=1)

# spec: error | runtime: TypeError | mypy: error | pyright: error | ty: error | pyrefly: error
# runtime: TypeError: Meta2.__new__() missing 1 required keyword-only argument: 'key'
Meta2("B", (), {})


class Meta3(type):
    # spec: ok | mypy: error (rejects an int-returning __new__ at the definition) | pyright: ok | ty: ok | pyrefly: ok
    def __new__(
        mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> int:
        return 0

    def __init__(cls, x: str) -> None:
        pass


# spec: ok | runtime: ok | mypy: error | pyright: ok | ty: ok | pyrefly: ok
assert_type(Meta3("C", (), {}), int)
```

Notes:

- pyright, ty, and pyrefly all honor the metametaclass `__call__()` returning
  `Never` and the `__init__()`-skipping rule when `__new__()` returns `int`
  (`reveal_type` confirms `Never` and `int` for ty and pyrefly). mypy evaluates
  `Meta1(...)` as `Meta1` and rejects the `Meta3.__new__()` definition outright.
- The direct call missing `key` is flagged by **all four** checkers — direct
  metaclass calls go through the standard constructor-call rules everywhere.

## The `type` Constructor — single-argument form inference

```python
from typing import assert_type


# spec: ok | runtime: ok | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
def func(x: int, y: int | str) -> None:
    assert_type(type(x), type[int])
    assert_type(type(y), type[int] | type[str])
```

All four checkers already special-case `type(obj)` to `type[T]`
(pyrefly reveals exactly `type[int]`; ty infers the even more precise class
literal `<class 'int'>` — see next example).

## The `type` Constructor — single-argument form on subclasses

```python
from typing import assert_type


class Meta(type):
    pass


# spec: ok | runtime: ok | mypy: ok | pyright: ok | ty: error | pyrefly: ok
assert_type(type(1), type[int])

# spec: error | runtime: TypeError | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
# runtime: TypeError: type.__new__() takes exactly 3 arguments (1 given)
Meta(1)

# spec: ok | runtime: ok | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
Meta("A", (), {})
```

Notes:

- **No checker currently reports `Meta(1)`**: all four inherit the
  single-argument overload of `type.__new__()`/`type.__init__()` into the
  subclass.
- ty's error on `assert_type(type(1), type[int])` is an artifact of it inferring
  the *more precise* class literal `<class 'int'>` for `type(1)` and reporting
  the mismatch as `assert-type-unspellable-subtype`; the inference itself is
  compliant.

## Class Statements — keyword arguments vs. the metaclass constructor

```python
from typing import Any


class Meta(type):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        key: int,
    ):
        return super().__new__(mcls, name, bases, namespace)


# spec: ok | runtime: ok | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
class MyClass1(metaclass=Meta, key=3):
    pass


# spec: error (wrong type for "key") | runtime: ok | mypy: ok | pyright: error | ty: ok | pyrefly: ok
class MyClass2(metaclass=Meta, key=""):
    pass


# spec: error (missing "key") | runtime: TypeError | mypy: ok | pyright: error | ty: ok | pyrefly: ok
# runtime: TypeError: Meta.__new__() missing 1 required keyword-only argument: 'key'
class MyClass3(metaclass=Meta):
    pass


# spec: ok | runtime: ok | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
Meta("MyClass4", (), {}, key=3)

# spec: error (wrong type for "key") | runtime: ok | mypy: error | pyright: error | ty: error | pyrefly: error
Meta("MyClass5", (), {}, key="")
```

Notes:

- Only pyright validates class-statement keyword arguments against a custom
  metaclass `__new__()` today. mypy, ty, and pyrefly all miss `MyClass2` and
  `MyClass3` — including the missing-argument case that fails at runtime.
- The equivalent *direct* calls are validated by all four checkers through the
  standard constructor-call rules.

## Class Statements — the implied `__prepare__` call

```python
from typing import Any


class Meta(type):
    # all four checkers report an override-incompatibility error at this
    # definition (parameter "**kwds" missing vs. type.__prepare__); that check
    # is unrelated to validating the implied __prepare__ call below
    @classmethod
    def __prepare__(mcls, name: str, bases: tuple[type, ...]):  # No **kwds
        return {}

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        key: int,
    ):
        return super().__new__(mcls, name, bases, namespace)


# spec: may error | runtime: TypeError | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
# runtime: TypeError: Meta.__prepare__() got an unexpected keyword argument 'key'
class MyClass6(metaclass=Meta, key=3):
    pass
```

No checker validates the implied `__prepare__` call at the class statement
(consistent with the spec's "may"). All four do flag the `__prepare__`
*definition* as an incompatible override of `type.__prepare__()`, which
indirectly catches this class of bug.

## The `__init_subclass__()` Method — no custom metaclass `__new__()`

```python
class Base:
    def __init_subclass__(cls, *, flag: bool = False) -> None:
        super().__init_subclass__()


# spec: ok | runtime: ok | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
class MyClass1(Base, flag=True):
    pass


# spec: error (wrong type for "flag") | runtime: ok | mypy: error | pyright: error | ty: error | pyrefly: ok
class MyClass2(Base, flag=""):
    pass


# spec: error (unknown argument) | runtime: TypeError | mypy: error | pyright: error | ty: error | pyrefly: ok
# runtime: TypeError: Base.__init_subclass__() got an unexpected keyword argument 'other'
class MyClass3(Base, other=1):
    pass


# spec: error (object.__init_subclass__ accepts no kwargs) | runtime: TypeError | mypy: error | pyright: error | ty: ok | pyrefly: ok
# runtime: TypeError: MyClass4.__init_subclass__() takes no keyword arguments
class MyClass4(other=1):
    pass
```

mypy, pyright, and ty implement this rule (ty misses only the
`object.__init_subclass__()` case); pyrefly performs no class-keyword validation.

## The `__init_subclass__()` Method — metaclass with only a custom `__init__()`

```python
from typing import Any


class Base:
    def __init_subclass__(cls, *, flag: bool = False) -> None:
        super().__init_subclass__()


class MetaInit(type):
    def __init__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        key: int,
    ) -> None:
        super().__init__(name, bases, namespace)


# spec: error | runtime: TypeError | mypy: ok | pyright: error | ty: error | pyrefly: ok
# runtime: TypeError: Base.__init_subclass__() got an unexpected keyword argument 'key'
class MyClass5(Base, metaclass=MetaInit, key=1):
    pass
```

`key` is accepted by `MetaInit.__init__()`, but `type.__new__()` (not
overridden) still forwards it to `Base.__init_subclass__()`, which rejects it.
pyright and ty report it; mypy and pyrefly do not.

## The `__init_subclass__()` Method — forwarding through direct calls and `**kwargs`

```python
from typing import Any


class Base:
    def __init_subclass__(cls, *, flag: bool = False) -> None:
        super().__init_subclass__()


# spec: ok | runtime: ok | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
type("D", (Base,), {}, flag=True)

# spec: may error | runtime: TypeError | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
# runtime: TypeError: Base.__init_subclass__() got an unexpected keyword argument 'other'
type("E", (Base,), {}, other=1)


class MetaKwargs(type):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ):
        return super().__new__(mcls, name, bases, namespace, **kwargs)


# spec: ok | runtime: ok | mypy: ok | pyright: ok | ty: ok | pyrefly: ok
class MyClass7(Base, metaclass=MetaKwargs, flag=True):
    pass


# spec: may error | runtime: TypeError | mypy: ok | pyright: ok | ty: error | pyrefly: ok
# runtime: TypeError: Base.__init_subclass__() got an unexpected keyword argument 'other'
class MyClass8(Base, metaclass=MetaKwargs, other=1):
    pass
```

No checker validates `__init_subclass__()` through a *direct* `type(...)` call.
Only ty follows the forwarding through a `**kwargs`-accepting metaclass
`__new__()` in a class statement, a consequence of ty checking
`__init_subclass__()` unconditionally — which also produces false positives
when a strict metaclass *consumes* a keyword argument (e.g.
`class C(Base, metaclass=MetaStrict, key=1)` where `key` never reaches
`__init_subclass__()`).

## Summary of divergences from the proposed spec text

| Rule | mypy | pyright | ty | pyrefly |
| --- | --- | --- | --- | --- |
| `type(obj)` evaluates to `type[T]` | yes | yes | yes (more precise) | yes |
| One-argument form rejected on `type` subclasses | no | no | no | no |
| Metametaclass `__call__()` governs metaclass calls | no | yes | yes | yes |
| `__init__()` skipped when metaclass `__new__()` returns non-instance | no | yes | yes | yes |
| Direct metaclass call arguments validated | yes | yes | yes | yes |
| Class-statement kwargs vs. custom metaclass `__new__()` | no | yes | no | no |
| Class-statement kwargs vs. `__init_subclass__()` (should) | yes | yes | mostly | no |
| `__init__()`-only metaclass still checks `__init_subclass__()` | no | yes | yes | no |
| `__prepare__()` implied call (may) | no | no | no | no |
| Direct-call `__init_subclass__()` forwarding (may) | no | no | no | no |
| `**kwargs` metaclass forwarding (may) | no | no | yes | no |
