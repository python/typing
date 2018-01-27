import sys
import os
import abc
import contextlib
import collections
import pickle
import subprocess
from unittest import TestCase, main, skipUnless
from typing import TypeVar, Optional
from typing import T, KT, VT  # Not in __all__.
from typing import Tuple, List
from typing import Generic
from typing import get_type_hints
from typing import no_type_check
from typing_extensions import NoReturn, ClassVar, Type, NewType
try:
    from typing_extensions import Protocol, runtime
except ImportError:
    pass
import typing
import typing_extensions
import collections.abc as collections_abc
OLD_GENERICS = False
try:
    from typing import _type_vars, _next_in_mro, _type_check
except ImportError:
    OLD_GENERICS = True

# We assume Python versions *below* 3.5.0 will have the most
# up-to-date version of the typing module installed. Since
# the typing module isn't a part of the standard library in older 
# versions of Python, those users are likely to have a reasonably
# modern version of `typing` installed from PyPi.
TYPING_LATEST = sys.version_info[:3] < (3, 5, 0)

# Flags used to mark tests that only apply after a specific
# version of the typing module.
TYPING_3_5_1 = TYPING_LATEST or sys.version_info[:3] >= (3, 5, 1)
TYPING_3_5_3 = TYPING_LATEST or sys.version_info[:3] >= (3, 5, 3)
TYPING_3_6_1 = TYPING_LATEST or sys.version_info[:3] >= (3, 6, 1)

# For typing versions where issubclass(...) and
# isinstance(...) checks are forbidden.
#
# See https://github.com/python/typing/issues/136
# and https://github.com/python/typing/pull/283
SUBCLASS_CHECK_FORBIDDEN = TYPING_3_5_3

# For typing versions where instantiating collection
# types are allowed.
#
# See https://github.com/python/typing/issues/367
CAN_INSTANTIATE_COLLECTIONS = TYPING_3_6_1

# For Python versions supporting async/await and friends.
ASYNCIO = sys.version_info[:2] >= (3, 5)

# For checks reliant on Python 3.6 syntax changes (e.g. classvar)
PY36 = sys.version_info[:2] >= (3, 6)

# Protocols are hard to backport to the original version of typing 3.5.0
HAVE_PROTOCOLS = sys.version_info[:3] != (3, 5, 0)


class BaseTestCase(TestCase):
    def assertIsSubclass(self, cls, class_or_tuple, msg=None):
        if not issubclass(cls, class_or_tuple):
            message = '%r is not a subclass of %r' % (cls, class_or_tuple)
            if msg is not None:
                message += ' : %s' % msg
            raise self.failureException(message)

    def assertNotIsSubclass(self, cls, class_or_tuple, msg=None):
        if issubclass(cls, class_or_tuple):
            message = '%r is a subclass of %r' % (cls, class_or_tuple)
            if msg is not None:
                message += ' : %s' % msg
            raise self.failureException(message)


class Employee:
    pass


class NoReturnTests(BaseTestCase):

    def test_noreturn_instance_type_error(self):
        with self.assertRaises(TypeError):
            isinstance(42, NoReturn)

    def test_noreturn_subclass_type_error_1(self):
        with self.assertRaises(TypeError):
            issubclass(Employee, NoReturn)

    @skipUnless(SUBCLASS_CHECK_FORBIDDEN, "Behavior added in typing 3.5.3")
    def test_noreturn_subclass_type_error_2(self):
        with self.assertRaises(TypeError):
            issubclass(NoReturn, Employee)

    def test_repr(self):
        if hasattr(typing, 'NoReturn'):
            self.assertEqual(repr(NoReturn), 'typing.NoReturn')
        else:
            self.assertEqual(repr(NoReturn), 'typing_extensions.NoReturn')

    def test_not_generic(self):
        with self.assertRaises(TypeError):
            NoReturn[int]

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class A(NoReturn):
                pass
        if SUBCLASS_CHECK_FORBIDDEN:
            with self.assertRaises(TypeError):
                class A(type(NoReturn)):
                    pass

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            NoReturn()
        with self.assertRaises(TypeError):
            type(NoReturn)()


class ClassVarTests(BaseTestCase):

    def test_basics(self):
        with self.assertRaises(TypeError):
            ClassVar[1]
        with self.assertRaises(TypeError):
            ClassVar[int, str]
        with self.assertRaises(TypeError):
            ClassVar[int][str]

    def test_repr(self):
        if hasattr(typing, 'ClassVar'):
            mod_name = 'typing'
        else:
            mod_name = 'typing_extensions'
        self.assertEqual(repr(ClassVar), mod_name + '.ClassVar')
        cv = ClassVar[int]
        self.assertEqual(repr(cv), mod_name + '.ClassVar[int]')
        cv = ClassVar[Employee]
        self.assertEqual(repr(cv), mod_name + '.ClassVar[%s.Employee]' % __name__)

    @skipUnless(SUBCLASS_CHECK_FORBIDDEN, "Behavior added in typing 3.5.3")
    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class C(type(ClassVar)):
                pass
        with self.assertRaises(TypeError):
            class C(type(ClassVar[int])):
                pass

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            ClassVar()
        with self.assertRaises(TypeError):
            type(ClassVar)()
        with self.assertRaises(TypeError):
            type(ClassVar[Optional[int]])()

    def test_no_isinstance(self):
        with self.assertRaises(TypeError):
            isinstance(1, ClassVar[int])
        with self.assertRaises(TypeError):
            issubclass(int, ClassVar)


class OverloadTests(BaseTestCase):

    def test_overload_fails(self):
        from typing_extensions import overload

        with self.assertRaises(RuntimeError):

            @overload
            def blah():
                pass

            blah()

    def test_overload_succeeds(self):
        from typing_extensions import overload

        @overload
        def blah():
            pass

        def blah():
            pass

        blah()


ASYNCIO_TESTS = """
import asyncio
from typing import Iterable
from typing_extensions import Awaitable, AsyncIterator

T_a = TypeVar('T_a')

class AwaitableWrapper(Awaitable[T_a]):

    def __init__(self, value):
        self.value = value

    def __await__(self) -> typing.Iterator[T_a]:
        yield
        return self.value

class AsyncIteratorWrapper(AsyncIterator[T_a]):

    def __init__(self, value: Iterable[T_a]):
        self.value = value

    def __aiter__(self) -> AsyncIterator[T_a]:
        return self

    @asyncio.coroutine
    def __anext__(self) -> T_a:
        data = yield from self.value
        if data:
            return data
        else:
            raise StopAsyncIteration

class ACM:
    async def __aenter__(self) -> int:
        return 42
    async def __aexit__(self, etype, eval, tb):
        return None
"""

if ASYNCIO:
    try:
        exec(ASYNCIO_TESTS)
    except ImportError:
        ASYNCIO = False
else:
    # fake names for the sake of static analysis
    asyncio = None
    AwaitableWrapper = AsyncIteratorWrapper = ACM = object

PY36_TESTS = """
from test import ann_module, ann_module2, ann_module3
from typing_extensions import AsyncContextManager
from typing import NamedTuple

class A:
    y: float
class B(A):
    x: ClassVar[Optional['B']] = None
    y: int
    b: int
class CSub(B):
    z: ClassVar['CSub'] = B()
class G(Generic[T]):
    lst: ClassVar[List[T]] = []

class NoneAndForward:
    parent: 'NoneAndForward'
    meaning: None

class XRepr(NamedTuple):
    x: int
    y: int = 1
    def __str__(self):
        return f'{self.x} -> {self.y}'
    def __add__(self, other):
        return 0

async def g_with(am: AsyncContextManager[int]):
    x: int
    async with am as x:
        return x

try:
    g_with(ACM()).send(None)
except StopIteration as e:
    assert e.args[0] == 42
"""

if PY36:
    exec(PY36_TESTS)
else:
    # fake names for the sake of static analysis
    ann_module = ann_module2 = ann_module3 = None
    A = B = CSub = G = CoolEmployee = CoolEmployeeWithDefault = object
    XMeth = XRepr = NoneAndForward = object

gth = get_type_hints


class GetTypeHintTests(BaseTestCase):
    @skipUnless(PY36, 'Python 3.6 required')
    def test_get_type_hints_modules(self):
        ann_module_type_hints = {1: 2, 'f': Tuple[int, int], 'x': int, 'y': str}
        self.assertEqual(gth(ann_module), ann_module_type_hints)
        self.assertEqual(gth(ann_module2), {})
        self.assertEqual(gth(ann_module3), {})

    @skipUnless(PY36, 'Python 3.6 required')
    def test_get_type_hints_classes(self):
        self.assertEqual(gth(ann_module.C, ann_module.__dict__),
                         {'y': Optional[ann_module.C]})
        self.assertIsInstance(gth(ann_module.j_class), dict)
        self.assertEqual(gth(ann_module.M), {'123': 123, 'o': type})
        self.assertEqual(gth(ann_module.D),
                         {'j': str, 'k': str, 'y': Optional[ann_module.C]})
        self.assertEqual(gth(ann_module.Y), {'z': int})
        self.assertEqual(gth(ann_module.h_class),
                         {'y': Optional[ann_module.C]})
        self.assertEqual(gth(ann_module.S), {'x': str, 'y': str})
        self.assertEqual(gth(ann_module.foo), {'x': int})
        self.assertEqual(gth(NoneAndForward, globals()),
                         {'parent': NoneAndForward, 'meaning': type(None)})

    @skipUnless(PY36, 'Python 3.6 required')
    def test_respect_no_type_check(self):
        @no_type_check
        class NoTpCheck:
            class Inn:
                def __init__(self, x: 'not a type'): ...
        self.assertTrue(NoTpCheck.__no_type_check__)
        self.assertTrue(NoTpCheck.Inn.__init__.__no_type_check__)
        self.assertEqual(gth(ann_module2.NTC.meth), {})
        class ABase(Generic[T]):
            def meth(x: int): ...
        @no_type_check
        class Der(ABase): ...
        self.assertEqual(gth(ABase.meth), {'x': int})

    @skipUnless(PY36, 'Python 3.6 required')
    def test_get_type_hints_ClassVar(self):
        self.assertEqual(gth(ann_module2.CV, ann_module2.__dict__),
                         {'var': ClassVar[ann_module2.CV]})
        self.assertEqual(gth(B, globals()),
                         {'y': int, 'x': ClassVar[Optional[B]], 'b': int})
        self.assertEqual(gth(CSub, globals()),
                         {'z': ClassVar[CSub], 'y': int, 'b': int,
                          'x': ClassVar[Optional[B]]})
        self.assertEqual(gth(G), {'lst': ClassVar[List[T]]})


class CollectionsAbcTests(BaseTestCase):

    def test_isinstance_collections(self):
        self.assertNotIsInstance(1, collections_abc.Mapping)
        self.assertNotIsInstance(1, collections_abc.Iterable)
        self.assertNotIsInstance(1, collections_abc.Container)
        self.assertNotIsInstance(1, collections_abc.Sized)
        if SUBCLASS_CHECK_FORBIDDEN:
            with self.assertRaises(TypeError):
                isinstance(collections.deque(), typing_extensions.Deque[int])
            with self.assertRaises(TypeError):
                issubclass(collections.Counter, typing_extensions.Counter[str])

    @skipUnless(ASYNCIO, 'Python 3.5 and multithreading required')
    def test_awaitable(self):
        ns = {}
        exec(
            "async def foo() -> typing_extensions.Awaitable[int]:\n"
            "    return await AwaitableWrapper(42)\n",
            globals(), ns)
        foo = ns['foo']
        g = foo()
        self.assertIsInstance(g, typing_extensions.Awaitable)
        self.assertNotIsInstance(foo, typing_extensions.Awaitable)
        g.send(None)  # Run foo() till completion, to avoid warning.

    @skipUnless(ASYNCIO, 'Python 3.5 and multithreading required')
    def test_coroutine(self):
        ns = {}
        exec(
            "async def foo():\n"
            "    return\n",
            globals(), ns)
        foo = ns['foo']
        g = foo()
        self.assertIsInstance(g, typing_extensions.Coroutine)
        with self.assertRaises(TypeError):
            isinstance(g, typing_extensions.Coroutine[int])
        self.assertNotIsInstance(foo, typing_extensions.Coroutine)
        try:
            g.send(None)
        except StopIteration:
            pass

    @skipUnless(ASYNCIO, 'Python 3.5 and multithreading required')
    def test_async_iterable(self):
        base_it = range(10)  # type: Iterator[int]
        it = AsyncIteratorWrapper(base_it)
        self.assertIsInstance(it, typing_extensions.AsyncIterable)
        self.assertIsInstance(it, typing_extensions.AsyncIterable)
        self.assertNotIsInstance(42, typing_extensions.AsyncIterable)

    @skipUnless(ASYNCIO, 'Python 3.5 and multithreading required')
    def test_async_iterator(self):
        base_it = range(10)  # type: Iterator[int]
        it = AsyncIteratorWrapper(base_it)
        if TYPING_3_5_1:
            self.assertIsInstance(it, typing_extensions.AsyncIterator)
        self.assertNotIsInstance(42, typing_extensions.AsyncIterator)

    def test_deque(self):
        self.assertIsSubclass(collections.deque, typing_extensions.Deque)
        class MyDeque(typing_extensions.Deque[int]): ...
        self.assertIsInstance(MyDeque(), collections.deque)

    def test_counter(self):
        self.assertIsSubclass(collections.Counter, typing_extensions.Counter)

    @skipUnless(CAN_INSTANTIATE_COLLECTIONS, "Behavior added in typing 3.6.1")
    def test_defaultdict_instantiation(self):
        self.assertIs(
            type(typing_extensions.DefaultDict()),
            collections.defaultdict)
        self.assertIs(
            type(typing_extensions.DefaultDict[KT, VT]()),
            collections.defaultdict)
        self.assertIs(
            type(typing_extensions.DefaultDict[str, int]()),
            collections.defaultdict)

    def test_defaultdict_subclass(self):

        class MyDefDict(typing_extensions.DefaultDict[str, int]):
            pass

        dd = MyDefDict()
        self.assertIsInstance(dd, MyDefDict)

        self.assertIsSubclass(MyDefDict, collections.defaultdict)
        if TYPING_3_5_3:
            self.assertNotIsSubclass(collections.defaultdict, MyDefDict)

    def test_chainmap_instantiation(self):
        self.assertIs(type(typing_extensions.ChainMap()), collections.ChainMap)
        self.assertIs(type(typing_extensions.ChainMap[KT, VT]()), collections.ChainMap)
        self.assertIs(type(typing_extensions.ChainMap[str, int]()), collections.ChainMap)
        class CM(typing_extensions.ChainMap[KT, VT]): ...
        if TYPING_3_5_3:
            self.assertIs(type(CM[int, str]()), CM)

    def test_chainmap_subclass(self):

        class MyChainMap(typing_extensions.ChainMap[str, int]):
            pass

        cm = MyChainMap()
        self.assertIsInstance(cm, MyChainMap)

        self.assertIsSubclass(MyChainMap, collections.ChainMap)
        if TYPING_3_5_3:
            self.assertNotIsSubclass(collections.ChainMap, MyChainMap)

    def test_deque_instantiation(self):
        self.assertIs(type(typing_extensions.Deque()), collections.deque)
        self.assertIs(type(typing_extensions.Deque[T]()), collections.deque)
        self.assertIs(type(typing_extensions.Deque[int]()), collections.deque)
        class D(typing_extensions.Deque[T]): ...
        if TYPING_3_5_3:
            self.assertIs(type(D[int]()), D)

    def test_counter_instantiation(self):
        self.assertIs(type(typing_extensions.Counter()), collections.Counter)
        self.assertIs(type(typing_extensions.Counter[T]()), collections.Counter)
        self.assertIs(type(typing_extensions.Counter[int]()), collections.Counter)
        class C(typing_extensions.Counter[T]): ...
        if TYPING_3_5_3:
            self.assertIs(type(C[int]()), C)
            self.assertEqual(C.__bases__, (typing_extensions.Counter,))

    def test_counter_subclass_instantiation(self):

        class MyCounter(typing_extensions.Counter[int]):
            pass

        d = MyCounter()
        self.assertIsInstance(d, MyCounter)
        self.assertIsInstance(d, collections.Counter)
        if TYPING_3_5_1:
            self.assertIsInstance(d, typing_extensions.Counter)

    @skipUnless(PY36, 'Python 3.6 required')
    def test_async_generator(self):
        ns = {}
        exec("async def f():\n"
             "    yield 42\n", globals(), ns)
        g = ns['f']()
        self.assertIsSubclass(type(g), typing_extensions.AsyncGenerator)

    @skipUnless(PY36, 'Python 3.6 required')
    def test_no_async_generator_instantiation(self):
        with self.assertRaises(TypeError):
            typing_extensions.AsyncGenerator()
        with self.assertRaises(TypeError):
            typing_extensions.AsyncGenerator[T, T]()
        with self.assertRaises(TypeError):
            typing_extensions.AsyncGenerator[int, int]()

    @skipUnless(PY36, 'Python 3.6 required')
    def test_subclassing_async_generator(self):
        class G(typing_extensions.AsyncGenerator[int, int]):
            def asend(self, value):
                pass
            def athrow(self, typ, val=None, tb=None):
                pass

        ns = {}
        exec('async def g(): yield 0', globals(), ns)
        g = ns['g']
        self.assertIsSubclass(G, typing_extensions.AsyncGenerator)
        self.assertIsSubclass(G, typing_extensions.AsyncIterable)
        self.assertIsSubclass(G, collections_abc.AsyncGenerator)
        self.assertIsSubclass(G, collections_abc.AsyncIterable)
        self.assertNotIsSubclass(type(g), G)

        instance = G()
        self.assertIsInstance(instance, typing_extensions.AsyncGenerator)
        self.assertIsInstance(instance, typing_extensions.AsyncIterable)
        self.assertIsInstance(instance, collections_abc.AsyncGenerator)
        self.assertIsInstance(instance, collections_abc.AsyncIterable)
        self.assertNotIsInstance(type(g), G)
        self.assertNotIsInstance(g, G)


class OtherABCTests(BaseTestCase):

    def test_contextmanager(self):
        @contextlib.contextmanager
        def manager():
            yield 42

        cm = manager()
        self.assertIsInstance(cm, typing_extensions.ContextManager)
        self.assertNotIsInstance(42, typing_extensions.ContextManager)

    @skipUnless(ASYNCIO, 'Python 3.5 required')
    def test_async_contextmanager(self):
        class NotACM:
            pass
        self.assertIsInstance(ACM(), typing_extensions.AsyncContextManager)
        self.assertNotIsInstance(NotACM(), typing_extensions.AsyncContextManager)
        @contextlib.contextmanager
        def manager():
            yield 42

        cm = manager()
        self.assertNotIsInstance(cm, typing_extensions.AsyncContextManager)
        if TYPING_3_5_3:
            self.assertEqual(typing_extensions.AsyncContextManager[int].__args__, (int,))
        if TYPING_3_6_1:
            with self.assertRaises(TypeError):
                isinstance(42, typing_extensions.AsyncContextManager[int])
        with self.assertRaises(TypeError):
            typing_extensions.AsyncContextManager[int, str]


class TypeTests(BaseTestCase):

    def test_type_basic(self):

        class User: pass
        class BasicUser(User): pass
        class ProUser(User): pass

        def new_user(user_class: Type[User]) -> User:
            return user_class()

        new_user(BasicUser)

    def test_type_typevar(self):

        class User: pass
        class BasicUser(User): pass
        class ProUser(User): pass

        U = TypeVar('U', bound=User)

        def new_user(user_class: Type[U]) -> U:
            return user_class()

        new_user(BasicUser)

    @skipUnless(sys.version_info[:3] != (3, 5, 2),
                'Python 3.5.2 has a somewhat buggy Type impl')
    def test_type_optional(self):
        A = Optional[Type[BaseException]]

        def foo(a: A) -> Optional[BaseException]:
            if a is None:
                return None
            else:
                return a()

        assert isinstance(foo(KeyboardInterrupt), KeyboardInterrupt)
        assert foo(None) is None


class NewTypeTests(BaseTestCase):

    def test_basic(self):
        UserId = NewType('UserId', int)
        UserName = NewType('UserName', str)
        self.assertIsInstance(UserId(5), int)
        self.assertIsInstance(UserName('Joe'), str)
        self.assertEqual(UserId(5) + 1, 6)

    def test_errors(self):
        UserId = NewType('UserId', int)
        UserName = NewType('UserName', str)
        with self.assertRaises(TypeError):
            issubclass(UserId, int)
        with self.assertRaises(TypeError):
            class D(UserName):
                pass


PY36_PROTOCOL_TESTS = """
class Coordinate(Protocol):
    x: int
    y: int

@runtime
class Point(Coordinate, Protocol):
    label: str

class MyPoint:
    x: int
    y: int
    label: str

class XAxis(Protocol):
    x: int

class YAxis(Protocol):
    y: int

@runtime
class Position(XAxis, YAxis, Protocol):
    pass

@runtime
class Proto(Protocol):
    attr: int
    def meth(self, arg: str) -> int:
        ...

class Concrete(Proto):
    pass

class Other:
    attr: int = 1
    def meth(self, arg: str) -> int:
        if arg == 'this':
            return 1
        return 0

class NT(NamedTuple):
    x: int
    y: int
"""

if PY36:
    exec(PY36_PROTOCOL_TESTS)
else:
    # fake names for the sake of static analysis
    Coordinate = Point = MyPoint = BadPoint = NT = object
    XAxis = YAxis = Position = Proto = Concrete = Other = object


if HAVE_PROTOCOLS:
    class ProtocolTests(BaseTestCase):

        def test_basic_protocol(self):
            @runtime
            class P(Protocol):
                def meth(self):
                    pass
            class C: pass
            class D:
                def meth(self):
                    pass
            self.assertIsSubclass(D, P)
            self.assertIsInstance(D(), P)
            self.assertNotIsSubclass(C, P)
            self.assertNotIsInstance(C(), P)

        def test_everything_implements_empty_protocol(self):
            @runtime
            class Empty(Protocol): pass
            class C: pass
            for thing in (object, type, tuple, C):
                self.assertIsSubclass(thing, Empty)
            for thing in (object(), 1, (), typing):
                self.assertIsInstance(thing, Empty)

        def test_no_inheritance_from_nominal(self):
            class C: pass
            class BP(Protocol): pass
            with self.assertRaises(TypeError):
                class P(C, Protocol):
                    pass
            with self.assertRaises(TypeError):
                class P(Protocol, C):
                    pass
            with self.assertRaises(TypeError):
                class P(BP, C, Protocol):
                    pass
            class D(BP, C): pass
            class E(C, BP): pass
            self.assertNotIsInstance(D(), E)
            self.assertNotIsInstance(E(), D)

        def test_no_instantiation(self):
            class P(Protocol): pass
            with self.assertRaises(TypeError):
                P()
            class C(P): pass
            self.assertIsInstance(C(), C)
            T = TypeVar('T')
            class PG(Protocol[T]): pass
            with self.assertRaises(TypeError):
                PG()
            with self.assertRaises(TypeError):
                PG[int]()
            with self.assertRaises(TypeError):
                PG[T]()
            class CG(PG[T]): pass
            self.assertIsInstance(CG[int](), CG)

        def test_cannot_instantiate_abstract(self):
            @runtime
            class P(Protocol):
                @abc.abstractmethod
                def ameth(self) -> int:
                    raise NotImplementedError
            class B(P):
                pass
            class C(B):
                def ameth(self) -> int:
                    return 26
            with self.assertRaises(TypeError):
                B()
            self.assertIsInstance(C(), P)

        def test_subprotocols_extending(self):
            class P1(Protocol):
                def meth1(self):
                    pass
            @runtime
            class P2(P1, Protocol):
                def meth2(self):
                    pass
            class C:
                def meth1(self):
                    pass
                def meth2(self):
                    pass
            class C1:
                def meth1(self):
                    pass
            class C2:
                def meth2(self):
                    pass
            self.assertNotIsInstance(C1(), P2)
            self.assertNotIsInstance(C2(), P2)
            self.assertNotIsSubclass(C1, P2)
            self.assertNotIsSubclass(C2, P2)
            self.assertIsInstance(C(), P2)
            self.assertIsSubclass(C, P2)

        def test_subprotocols_merging(self):
            class P1(Protocol):
                def meth1(self):
                    pass
            class P2(Protocol):
                def meth2(self):
                    pass
            @runtime
            class P(P1, P2, Protocol):
                pass
            class C:
                def meth1(self):
                    pass
                def meth2(self):
                    pass
            class C1:
                def meth1(self):
                    pass
            class C2:
                def meth2(self):
                    pass
            self.assertNotIsInstance(C1(), P)
            self.assertNotIsInstance(C2(), P)
            self.assertNotIsSubclass(C1, P)
            self.assertNotIsSubclass(C2, P)
            self.assertIsInstance(C(), P)
            self.assertIsSubclass(C, P)

        def test_protocols_issubclass(self):
            T = TypeVar('T')
            @runtime
            class P(Protocol):
                def x(self): ...
            @runtime
            class PG(Protocol[T]):
                def x(self): ...
            class BadP(Protocol):
                def x(self): ...
            class BadPG(Protocol[T]):
                def x(self): ...
            class C:
                def x(self): ...
            self.assertIsSubclass(C, P)
            self.assertIsSubclass(C, PG)
            self.assertIsSubclass(BadP, PG)
            self.assertIsSubclass(PG[int], PG)
            self.assertIsSubclass(BadPG[int], P)
            self.assertIsSubclass(BadPG[T], PG)
            with self.assertRaises(TypeError):
                issubclass(C, PG[T])
            with self.assertRaises(TypeError):
                issubclass(C, PG[C])
            with self.assertRaises(TypeError):
                issubclass(C, BadP)
            with self.assertRaises(TypeError):
                issubclass(C, BadPG)
            with self.assertRaises(TypeError):
                issubclass(P, PG[T])
            with self.assertRaises(TypeError):
                issubclass(PG, PG[int])

        def test_protocols_issubclass_non_callable(self):
            class C:
                x = 1
            @runtime
            class PNonCall(Protocol):
                x = 1
            with self.assertRaises(TypeError):
                issubclass(C, PNonCall)
            self.assertIsInstance(C(), PNonCall)
            PNonCall.register(C)
            with self.assertRaises(TypeError):
                issubclass(C, PNonCall)
            self.assertIsInstance(C(), PNonCall)
            # check that non-protocol subclasses are not affected
            class D(PNonCall): ...
            self.assertNotIsSubclass(C, D)
            self.assertNotIsInstance(C(), D)
            D.register(C)
            self.assertIsSubclass(C, D)
            self.assertIsInstance(C(), D)
            with self.assertRaises(TypeError):
                issubclass(D, PNonCall)

        def test_protocols_isinstance(self):
            T = TypeVar('T')
            @runtime
            class P(Protocol):
                def meth(x): ...
            @runtime
            class PG(Protocol[T]):
                def meth(x): ...
            class BadP(Protocol):
                def meth(x): ...
            class BadPG(Protocol[T]):
                def meth(x): ...
            class C:
                def meth(x): ...
            self.assertIsInstance(C(), P)
            self.assertIsInstance(C(), PG)
            with self.assertRaises(TypeError):
                isinstance(C(), PG[T])
            with self.assertRaises(TypeError):
                isinstance(C(), PG[C])
            with self.assertRaises(TypeError):
                isinstance(C(), BadP)
            with self.assertRaises(TypeError):
                isinstance(C(), BadPG)

        @skipUnless(PY36, 'Python 3.6 required')
        def test_protocols_isinstance_py36(self):
            class APoint:
                def __init__(self, x, y, label):
                    self.x = x
                    self.y = y
                    self.label = label
            class BPoint:
                label = 'B'
                def __init__(self, x, y):
                    self.x = x
                    self.y = y
            class C:
                def __init__(self, attr):
                    self.attr = attr
                def meth(self, arg):
                    return 0
            class Bad: pass
            self.assertIsInstance(APoint(1, 2, 'A'), Point)
            self.assertIsInstance(BPoint(1, 2), Point)
            self.assertNotIsInstance(MyPoint(), Point)
            self.assertIsInstance(BPoint(1, 2), Position)
            self.assertIsInstance(Other(), Proto)
            self.assertIsInstance(Concrete(), Proto)
            self.assertIsInstance(C(42), Proto)
            self.assertNotIsInstance(Bad(), Proto)
            self.assertNotIsInstance(Bad(), Point)
            self.assertNotIsInstance(Bad(), Position)
            self.assertNotIsInstance(Bad(), Concrete)
            self.assertNotIsInstance(Other(), Concrete)
            self.assertIsInstance(NT(1, 2), Position)

        def test_protocols_isinstance_init(self):
            T = TypeVar('T')
            @runtime
            class P(Protocol):
                x = 1
            @runtime
            class PG(Protocol[T]):
                x = 1
            class C:
                def __init__(self, x):
                    self.x = x
            self.assertIsInstance(C(1), P)
            self.assertIsInstance(C(1), PG)

        def test_protocols_support_register(self):
            @runtime
            class P(Protocol):
                x = 1
            class PM(Protocol):
                def meth(self): pass
            class D(PM): pass
            class C: pass
            D.register(C)
            P.register(C)
            self.assertIsInstance(C(), P)
            self.assertIsInstance(C(), D)

        def test_none_on_non_callable_doesnt_block_implementation(self):
            @runtime
            class P(Protocol):
                x = 1
            class A:
                x = 1
            class B(A):
                x = None
            class C:
                def __init__(self):
                    self.x = None
            self.assertIsInstance(B(), P)
            self.assertIsInstance(C(), P)

        def test_none_on_callable_blocks_implementation(self):
            @runtime
            class P(Protocol):
                def x(self): ...
            class A:
                def x(self): ...
            class B(A):
                x = None
            class C:
                def __init__(self):
                    self.x = None
            self.assertNotIsInstance(B(), P)
            self.assertNotIsInstance(C(), P)

        def test_non_protocol_subclasses(self):
            class P(Protocol):
                x = 1
            @runtime
            class PR(Protocol):
                def meth(self): pass
            class NonP(P):
                x = 1
            class NonPR(PR): pass
            class C:
                x = 1
            class D:
                def meth(self): pass
            self.assertNotIsInstance(C(), NonP)
            self.assertNotIsInstance(D(), NonPR)
            self.assertNotIsSubclass(C, NonP)
            self.assertNotIsSubclass(D, NonPR)
            self.assertIsInstance(NonPR(), PR)
            self.assertIsSubclass(NonPR, PR)

        def test_custom_subclasshook(self):
            class P(Protocol):
                x = 1
            class OKClass: pass
            class BadClass:
                x = 1
            class C(P):
                @classmethod
                def __subclasshook__(cls, other):
                    return other.__name__.startswith("OK")
            self.assertIsInstance(OKClass(), C)
            self.assertNotIsInstance(BadClass(), C)
            self.assertIsSubclass(OKClass, C)
            self.assertNotIsSubclass(BadClass, C)

        def test_issubclass_fails_correctly(self):
            @runtime
            class P(Protocol):
                x = 1
            class C: pass
            with self.assertRaises(TypeError):
                issubclass(C(), P)

        @skipUnless(not OLD_GENERICS, "New style generics required")
        def test_defining_generic_protocols(self):
            T = TypeVar('T')
            S = TypeVar('S')
            @runtime
            class PR(Protocol[T, S]):
                def meth(self): pass
            class P(PR[int, T], Protocol[T]):
                y = 1
            self.assertIsSubclass(PR[int, T], PR)
            self.assertIsSubclass(P[str], PR)
            with self.assertRaises(TypeError):
                PR[int]
            with self.assertRaises(TypeError):
                P[int, str]
            with self.assertRaises(TypeError):
                PR[int, 1]
            if TYPING_3_5_3:
                with self.assertRaises(TypeError):
                    PR[int, ClassVar]
            class C(PR[int, T]): pass
            self.assertIsInstance(C[str](), C)

        def test_defining_generic_protocols_old_style(self):
            T = TypeVar('T')
            S = TypeVar('S')
            @runtime
            class PR(Protocol, Generic[T, S]):
                def meth(self): pass
            class P(PR[int, str], Protocol):
                y = 1
            self.assertIsSubclass(PR[int, str], PR)
            self.assertIsSubclass(P, PR)
            with self.assertRaises(TypeError):
                PR[int]
            with self.assertRaises(TypeError):
                PR[int, 1]
            class P1(Protocol, Generic[T]):
                def bar(self, x: T) -> str: ...
            class P2(Generic[T], Protocol):
                def bar(self, x: T) -> str: ...
            @runtime
            class PSub(P1[str], Protocol):
                x = 1
            class Test:
                x = 1
                def bar(self, x: str) -> str:
                    return x
            self.assertIsInstance(Test(), PSub)
            if TYPING_3_5_3:
                with self.assertRaises(TypeError):
                    PR[int, ClassVar]

        def test_init_called(self):
            T = TypeVar('T')
            class P(Protocol[T]): pass
            class C(P[T]):
                def __init__(self):
                    self.test = 'OK'
            self.assertEqual(C[int]().test, 'OK')

        @skipUnless(not OLD_GENERICS, "New style generics required")
        def test_protocols_bad_subscripts(self):
            T = TypeVar('T')
            S = TypeVar('S')
            with self.assertRaises(TypeError):
                class P(Protocol[T, T]): pass
            with self.assertRaises(TypeError):
                class P(Protocol[int]): pass
            with self.assertRaises(TypeError):
                class P(Protocol[T], Protocol[S]): pass
            with self.assertRaises(TypeError):
                class P(typing.Mapping[T, S], Protocol[T]): pass

        @skipUnless(TYPING_3_5_3, 'New style __repr__ and __eq__ only')
        def test_generic_protocols_repr(self):
            T = TypeVar('T')
            S = TypeVar('S')
            class P(Protocol[T, S]): pass
            self.assertTrue(repr(P).endswith('P'))
            self.assertTrue(repr(P[T, S]).endswith('P[~T, ~S]'))
            self.assertTrue(repr(P[int, str]).endswith('P[int, str]'))

        @skipUnless(TYPING_3_5_3, 'New style __repr__ and __eq__ only')
        def test_generic_protocols_eq(self):
            T = TypeVar('T')
            S = TypeVar('S')
            class P(Protocol[T, S]): pass
            self.assertEqual(P, P)
            self.assertEqual(P[int, T], P[int, T])
            self.assertEqual(P[T, T][Tuple[T, S]][int, str],
                             P[Tuple[int, str], Tuple[int, str]])

        @skipUnless(not OLD_GENERICS, "New style generics required")
        def test_generic_protocols_special_from_generic(self):
            T = TypeVar('T')
            class P(Protocol[T]): pass
            self.assertEqual(P.__parameters__, (T,))
            self.assertIs(P.__args__, None)
            self.assertIs(P.__origin__, None)
            self.assertEqual(P[int].__parameters__, ())
            self.assertEqual(P[int].__args__, (int,))
            self.assertIs(P[int].__origin__, P)

        def test_generic_protocols_special_from_protocol(self):
            @runtime
            class PR(Protocol):
                x = 1
            class P(Protocol):
                def meth(self):
                    pass
            T = TypeVar('T')
            class PG(Protocol[T]):
                x = 1
                def meth(self):
                    pass
            self.assertTrue(P._is_protocol)
            self.assertTrue(PR._is_protocol)
            self.assertTrue(PG._is_protocol)
            with self.assertRaises(AttributeError):
                self.assertFalse(P._is_runtime_protocol)
            self.assertTrue(PR._is_runtime_protocol)
            self.assertTrue(PG[int]._is_protocol)
            self.assertEqual(P._get_protocol_attrs(), {'meth'})
            self.assertEqual(PR._get_protocol_attrs(), {'x'})
            self.assertEqual(frozenset(PG._get_protocol_attrs()),
                             frozenset({'x', 'meth'}))
            self.assertEqual(frozenset(PG[int]._get_protocol_attrs()),
                             frozenset({'x', 'meth'}))

        def test_no_runtime_deco_on_nominal(self):
            with self.assertRaises(TypeError):
                @runtime
                class C: pass
            class Proto(Protocol):
                x = 1
            with self.assertRaises(TypeError):
                @runtime
                class Concrete(Proto):
                    pass

        def test_none_treated_correctly(self):
            @runtime
            class P(Protocol):
                x = None  # type: int
            class B(object): pass
            self.assertNotIsInstance(B(), P)
            class C:
                x = 1
            class D:
                x = None
            self.assertIsInstance(C(), P)
            self.assertIsInstance(D(), P)
            class CI:
                def __init__(self):
                    self.x = 1
            class DI:
                def __init__(self):
                    self.x = None
            self.assertIsInstance(C(), P)
            self.assertIsInstance(D(), P)

        def test_protocols_in_unions(self):
            class P(Protocol):
                x = None  # type: int
            Alias = typing.Union[typing.Iterable, P]
            Alias2 = typing.Union[P, typing.Iterable]
            self.assertEqual(Alias, Alias2)

        def test_protocols_pickleable(self):
            global P, CP  # pickle wants to reference the class by name
            T = TypeVar('T')

            @runtime
            class P(Protocol[T]):
                x = 1
            class CP(P[int]):
                pass

            c = CP()
            c.foo = 42
            c.bar = 'abc'
            for proto in range(pickle.HIGHEST_PROTOCOL + 1):
                z = pickle.dumps(c, proto)
                x = pickle.loads(z)
                self.assertEqual(x.foo, 42)
                self.assertEqual(x.bar, 'abc')
                self.assertEqual(x.x, 1)
                self.assertEqual(x.__dict__, {'foo': 42, 'bar': 'abc'})
                s = pickle.dumps(P)
                D = pickle.loads(s)
                class E:
                    x = 1
                self.assertIsInstance(E(), D)


class AllTests(BaseTestCase):

    def test_typing_extensions_includes_standard(self):
        a = typing_extensions.__all__
        self.assertIn('ClassVar', a)
        self.assertIn('Type', a)
        self.assertIn('ChainMap', a)
        self.assertIn('ContextManager', a)
        self.assertIn('Counter', a)
        self.assertIn('DefaultDict', a)
        self.assertIn('Deque', a)
        self.assertIn('NewType', a)
        self.assertIn('overload', a)
        self.assertIn('Text', a)
        self.assertIn('TYPE_CHECKING', a)

        if ASYNCIO:
            self.assertIn('Awaitable', a)
            self.assertIn('AsyncIterator', a)
            self.assertIn('AsyncIterable', a)
            self.assertIn('Coroutine', a)
            self.assertIn('AsyncContextManager', a)

        if PY36:
            self.assertIn('AsyncGenerator', a)

        if TYPING_3_5_3:
            self.assertIn('Protocol', a)
            self.assertIn('runtime', a)

    def test_typing_extensions_defers_when_possible(self):
        exclude = {'overload', 'Text', 'TYPE_CHECKING'}
        for item in typing_extensions.__all__:
            if item not in exclude and hasattr(typing, item):
                self.assertIs(
                    getattr(typing_extensions, item),
                    getattr(typing, item))

    def test_typing_extensions_compiles_with_opt(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'typing_extensions.py')
        try:
            subprocess.check_output('python -OO {}'.format(file_path),
                                    stderr=subprocess.STDOUT,
                                    shell=True)
        except subprocess.CalledProcessError:
            self.fail('Module does not compile with optimize=2 (-OO flag).')


if __name__ == '__main__':
   main()
