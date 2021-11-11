import sys
import os
import abc
import collections
import collections.abc
import pickle
import subprocess
import types
from unittest import TestCase, main, skipIf
from test import ann_module, ann_module2, ann_module3
import typing
import typing_extensions as te
from typing_extensions import get_type_hints as gth

try:
    from typing import _get_protocol_attrs  # 3.8+
except ImportError:
    from typing_extensions import _get_protocol_attrs  # 3.7

T = typing.TypeVar('T')  # Any type.
KT = typing.TypeVar('KT')  # Key type.
VT = typing.TypeVar('VT')  # Value type.

# Flags used to mark tests that only apply after a specific
# version of the typing module.
TYPING_3_10_0 = sys.version_info[:3] >= (3, 10, 0)
TYPING_3_11_0 = sys.version_info[:3] >= (3, 11, 0)


class Employee:
    pass


class BaseTestCase(TestCase):
    def assertIsSubclass(self, cls, class_or_tuple, msg=None):
        if not issubclass(cls, class_or_tuple):
            message = f'{cls!r} is not a subclass of {repr(class_or_tuple)}'
            if msg is not None:
                message += f' : {msg}'
            raise self.failureException(message)

    def assertNotIsSubclass(self, cls, class_or_tuple, msg=None):
        if issubclass(cls, class_or_tuple):
            message = f'{cls!r} is a subclass of {repr(class_or_tuple)}'
            if msg is not None:
                message += f' : {msg}'
            raise self.failureException(message)


class FinalTests(BaseTestCase):

    def test_basics(self):
        with self.assertRaises(TypeError):
            te.Final[1]
        with self.assertRaises(TypeError):
            te.Final[int, str]
        with self.assertRaises(TypeError):
            te.Final[int][str]

    def test_repr(self):
        if hasattr(typing, 'Final'):
            mod_name = 'typing'
        else:
            mod_name = 'typing_extensions'
        self.assertEqual(repr(te.Final), mod_name + '.Final')
        cv = te.Final[int]
        self.assertEqual(repr(cv), mod_name + '.Final[int]')
        cv = te.Final[Employee]
        self.assertEqual(repr(cv), mod_name + f'.Final[{__name__}.Employee]')

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class C(type(te.Final)):
                pass
        with self.assertRaises(TypeError):
            class C(type(te.Final[int])):
                pass

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            te.Final()
        with self.assertRaises(TypeError):
            type(te.Final)()
        with self.assertRaises(TypeError):
            type(te.Final[typing.Optional[int]])()

    def test_no_isinstance(self):
        with self.assertRaises(TypeError):
            isinstance(1, te.Final[int])
        with self.assertRaises(TypeError):
            issubclass(int, te.Final)


class RequiredTests(BaseTestCase):

    def test_basics(self):
        with self.assertRaises(TypeError):
            te.Required[1]
        with self.assertRaises(TypeError):
            te.Required[int, str]
        with self.assertRaises(TypeError):
            te.Required[int][str]

    def test_repr(self):
        if hasattr(typing, 'Required'):
            mod_name = 'typing'
        else:
            mod_name = 'typing_extensions'
        self.assertEqual(repr(te.Required), mod_name + '.Required')
        cv = te.Required[int]
        self.assertEqual(repr(cv), mod_name + '.Required[int]')
        cv = te.Required[Employee]
        self.assertEqual(repr(cv), mod_name + '.Required[%s.Employee]' % __name__)

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class C(type(te.Required)):
                pass
        with self.assertRaises(TypeError):
            class C(type(te.Required[int])):
                pass

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            te.Required()
        with self.assertRaises(TypeError):
            type(te.Required)()
        with self.assertRaises(TypeError):
            type(te.Required[typing.Optional[int]])()

    def test_no_isinstance(self):
        with self.assertRaises(TypeError):
            isinstance(1, te.Required[int])
        with self.assertRaises(TypeError):
            issubclass(int, te.Required)


class NotRequiredTests(BaseTestCase):

    def test_basics(self):
        with self.assertRaises(TypeError):
            te.NotRequired[1]
        with self.assertRaises(TypeError):
            te.NotRequired[int, str]
        with self.assertRaises(TypeError):
            te.NotRequired[int][str]

    def test_repr(self):
        if hasattr(typing, 'NotRequired'):
            mod_name = 'typing'
        else:
            mod_name = 'typing_extensions'
        self.assertEqual(repr(te.NotRequired), mod_name + '.NotRequired')
        cv = te.NotRequired[int]
        self.assertEqual(repr(cv), mod_name + '.NotRequired[int]')
        cv = te.NotRequired[Employee]
        self.assertEqual(repr(cv), mod_name + '.NotRequired[%s.Employee]' % __name__)

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class C(type(te.NotRequired)):
                pass
        with self.assertRaises(TypeError):
            class C(type(te.NotRequired[int])):
                pass

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            te.NotRequired()
        with self.assertRaises(TypeError):
            type(te.NotRequired)()
        with self.assertRaises(TypeError):
            type(te.NotRequired[typing.Optional[int]])()

    def test_no_isinstance(self):
        with self.assertRaises(TypeError):
            isinstance(1, te.NotRequired[int])
        with self.assertRaises(TypeError):
            issubclass(int, te.NotRequired)


class IntVarTests(BaseTestCase):
    def test_valid(self):
        T_ints = te.IntVar("T_ints")  # noqa

    def test_invalid(self):
        with self.assertRaises(TypeError):
            T_ints = te.IntVar("T_ints", int)
        with self.assertRaises(TypeError):
            T_ints = te.IntVar("T_ints", bound=int)
        with self.assertRaises(TypeError):
            T_ints = te.IntVar("T_ints", covariant=True)  # noqa


class LiteralTests(BaseTestCase):
    def test_basics(self):
        te.Literal[1]
        te.Literal[1, 2, 3]
        te.Literal["x", "y", "z"]
        te.Literal[None]

    def test_illegal_parameters_do_not_raise_runtime_errors(self):
        # Type checkers should reject these types, but we do not
        # raise errors at runtime to maintain maximum flexibility
        te.Literal[int]
        te.Literal[te.Literal[1, 2], te.Literal[4, 5]]
        te.Literal[3j + 2, ..., ()]
        te.Literal[b"foo", u"bar"]
        te.Literal[{"foo": 3, "bar": 4}]
        te.Literal[T]

    def test_literals_inside_other_types(self):
        typing.List[te.Literal[1, 2, 3]]
        typing.List[te.Literal[("foo", "bar", "baz")]]

    def test_repr(self):
        if hasattr(typing, 'Literal'):
            mod_name = 'typing'
        else:
            mod_name = 'typing_extensions'
        self.assertEqual(repr(te.Literal[1]), mod_name + ".Literal[1]")
        self.assertEqual(repr(te.Literal[1, True, "foo"]), mod_name + ".Literal[1, True, 'foo']")
        self.assertEqual(repr(te.Literal[int]), mod_name + ".Literal[int]")
        self.assertEqual(repr(te.Literal), mod_name + ".Literal")
        self.assertEqual(repr(te.Literal[None]), mod_name + ".Literal[None]")

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            te.Literal()
        with self.assertRaises(TypeError):
            te.Literal[1]()
        with self.assertRaises(TypeError):
            type(te.Literal)()
        with self.assertRaises(TypeError):
            type(te.Literal[1])()

    def test_no_isinstance_or_issubclass(self):
        with self.assertRaises(TypeError):
            isinstance(1, te.Literal[1])
        with self.assertRaises(TypeError):
            isinstance(int, te.Literal[1])
        with self.assertRaises(TypeError):
            issubclass(1, te.Literal[1])
        with self.assertRaises(TypeError):
            issubclass(int, te.Literal[1])

    def test_no_subclassing(self):
        with self.assertRaises(TypeError):
            class Foo(te.Literal[1]): pass
        with self.assertRaises(TypeError):
            class Bar(te.Literal): pass

    def test_no_multiple_subscripts(self):
        with self.assertRaises(TypeError):
            te.Literal[1][1]


class GetUtilitiesTestCase(TestCase):
    def test_get_origin(self):
        T = typing.TypeVar('T')
        P = te.ParamSpec('P')
        class C(typing.Generic[T]): pass
        self.assertIs(te.get_origin(C[int]), C)
        self.assertIs(te.get_origin(C[T]), C)
        self.assertIs(te.get_origin(int), None)
        self.assertIs(te.get_origin(typing.ClassVar[int]), typing.ClassVar)
        self.assertIs(te.get_origin(typing.Union[int, str]), typing.Union)
        self.assertIs(te.get_origin(te.Literal[42, 43]), te.Literal)
        self.assertIs(te.get_origin(te.Final[typing.List[int]]), te.Final)
        self.assertIs(te.get_origin(typing.Generic), typing.Generic)
        self.assertIs(te.get_origin(typing.Generic[T]), typing.Generic)
        self.assertIs(te.get_origin(typing.List[typing.Tuple[T, T]][int]), list)
        self.assertIs(te.get_origin(te.Annotated[T, 'thing']), te.Annotated)
        self.assertIs(te.get_origin(typing.List), list)
        self.assertIs(te.get_origin(typing.Tuple), tuple)
        self.assertIs(te.get_origin(typing.Callable), collections.abc.Callable)
        if sys.version_info >= (3, 9):
            self.assertIs(te.get_origin(list[int]), list)
        self.assertIs(te.get_origin(list), None)
        self.assertIs(te.get_origin(P.args), P)
        self.assertIs(te.get_origin(P.kwargs), P)

    def test_get_args(self):
        T = typing.TypeVar('T')
        class C(typing.Generic[T]): pass
        self.assertEqual(te.get_args(C[int]), (int,))
        self.assertEqual(te.get_args(C[T]), (T,))
        self.assertEqual(te.get_args(int), ())
        self.assertEqual(te.get_args(typing.ClassVar[int]), (int,))
        self.assertEqual(te.get_args(typing.Union[int, str]), (int, str))
        self.assertEqual(te.get_args(te.Literal[42, 43]), (42, 43))
        self.assertEqual(te.get_args(te.Final[typing.List[int]]), (typing.List[int],))
        self.assertEqual(te.get_args(typing.Union[int, typing.Tuple[T, int]][str]),
                         (int, typing.Tuple[str, int]))
        self.assertEqual(te.get_args(typing.Dict[int, typing.Tuple[T, T]][typing.Optional[int]]),
                         (int, typing.Tuple[typing.Optional[int], typing.Optional[int]]))
        self.assertEqual(te.get_args(typing.Callable[[], T][int]), ([], int))
        self.assertEqual(te.get_args(typing.Callable[..., int]), (..., int))
        self.assertEqual(te.get_args(typing.Union[int, typing.Callable[[typing.Tuple[T, ...]], str]]),
                         (int, typing.Callable[[typing.Tuple[T, ...]], str]))
        self.assertEqual(te.get_args(typing.Tuple[int, ...]), (int, ...))
        self.assertEqual(te.get_args(typing.Tuple[()]), ((),))
        self.assertEqual(te.get_args(te.Annotated[T, 'one', 2, ['three']]), (T, 'one', 2, ['three']))
        self.assertEqual(te.get_args(typing.List), ())
        self.assertEqual(te.get_args(typing.Tuple), ())
        self.assertEqual(te.get_args(typing.Callable), ())
        if sys.version_info >= (3, 9):
            self.assertEqual(te.get_args(list[int]), (int,))
        self.assertEqual(te.get_args(list), ())
        if sys.version_info >= (3, 9):
            # Support Python versions with and without the fix for
            # https://bugs.python.org/issue42195
            # The first variant is for 3.9.2+, the second for 3.9.0 and 1
            self.assertIn(te.get_args(collections.abc.Callable[[int], str]),
                          (([int], str), ([[int]], str)))
            self.assertIn(te.get_args(collections.abc.Callable[[], str]),
                          (([], str), ([[]], str)))
            self.assertEqual(te.get_args(collections.abc.Callable[..., str]), (..., str))
        P = te.ParamSpec('P')
        # In 3.9 and lower we use typing_extensions's hacky implementation
        # of ParamSpec, which gets incorrectly wrapped in a list
        self.assertIn(te.get_args(typing.Callable[P, int]), [(P, int), ([P], int)])
        self.assertEqual(te.get_args(typing.Callable[te.Concatenate[int, P], int]),
                         (te.Concatenate[int, P], int))


class OrderedDictTests(BaseTestCase):
    def test_ordereddict_instantiation(self):
        self.assertIs(
            type(te.OrderedDict()),
            collections.OrderedDict)
        self.assertIs(
            type(te.OrderedDict[KT, VT]()),
            collections.OrderedDict)
        self.assertIs(
            type(te.OrderedDict[str, int]()),
            collections.OrderedDict)

    def test_ordereddict_subclass(self):

        class MyOrdDict(te.OrderedDict[str, int]):
            pass

        od = MyOrdDict()
        self.assertIsInstance(od, MyOrdDict)

        self.assertIsSubclass(MyOrdDict, collections.OrderedDict)
        self.assertNotIsSubclass(collections.OrderedDict, MyOrdDict)


class ProtocolTests(BaseTestCase):

    def test_basic_protocol(self):
        @te.runtime_checkable
        class P(te.Protocol):
            def meth(self):
                pass
        class C: pass
        class D:
            def meth(self):
                pass
        def f():
            pass
        self.assertIsSubclass(D, P)
        self.assertIsInstance(D(), P)
        self.assertNotIsSubclass(C, P)
        self.assertNotIsInstance(C(), P)
        self.assertNotIsSubclass(types.FunctionType, P)
        self.assertNotIsInstance(f, P)

    def test_everything_implements_empty_protocol(self):
        @te.runtime_checkable
        class Empty(te.Protocol): pass
        class C: pass
        def f():
            pass
        for thing in (object, type, tuple, C, types.FunctionType):
            self.assertIsSubclass(thing, Empty)
        for thing in (object(), 1, (), typing, f):
            self.assertIsInstance(thing, Empty)

    def test_function_implements_protocol(self):
        @te.runtime_checkable
        class HasCallProtocol(te.Protocol):
            __call__: typing.Callable
        def f():
            pass
        self.assertIsInstance(f, HasCallProtocol)

    def test_no_inheritance_from_nominal(self):
        class C: pass
        class BP(te.Protocol): pass
        with self.assertRaises(TypeError):
            class P(C, te.Protocol):
                pass
        with self.assertRaises(TypeError):
            class P(te.Protocol, C):
                pass
        with self.assertRaises(TypeError):
            class P(BP, C, te.Protocol):
                pass
        class D(BP, C): pass
        class E(C, BP): pass
        self.assertNotIsInstance(D(), E)
        self.assertNotIsInstance(E(), D)

    def test_no_instantiation(self):
        class P(te.Protocol): pass
        with self.assertRaises(TypeError):
            P()
        class C(P): pass
        self.assertIsInstance(C(), C)
        T = typing.TypeVar('T')
        class PG(te.Protocol[T]): pass
        with self.assertRaises(TypeError):
            PG()
        with self.assertRaises(TypeError):
            PG[int]()
        with self.assertRaises(TypeError):
            PG[T]()
        class CG(PG[T]): pass
        self.assertIsInstance(CG[int](), CG)

    def test_cannot_instantiate_abstract(self):
        @te.runtime_checkable
        class P(te.Protocol):
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
        class P1(te.Protocol):
            def meth1(self):
                pass
        @te.runtime_checkable
        class P2(P1, te.Protocol):
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
        class P1(te.Protocol):
            def meth1(self):
                pass
        class P2(te.Protocol):
            def meth2(self):
                pass
        @te.runtime_checkable
        class P(P1, P2, te.Protocol):
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
        T = typing.TypeVar('T')
        @te.runtime_checkable
        class P(te.Protocol):
            def x(self): ...
        @te.runtime_checkable
        class PG(te.Protocol[T]):
            def x(self): ...
        class BadP(te.Protocol):
            def x(self): ...
        class BadPG(te.Protocol[T]):
            def x(self): ...
        class C:
            def x(self): ...
        self.assertIsSubclass(C, P)
        self.assertIsSubclass(C, PG)
        self.assertIsSubclass(BadP, PG)
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
        @te.runtime_checkable
        class PNonCall(te.Protocol):
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
        T = typing.TypeVar('T')
        @te.runtime_checkable
        class P(te.Protocol):
            def meth(x): ...
        @te.runtime_checkable
        class PG(te.Protocol[T]):
            def meth(x): ...
        class BadP(te.Protocol):
            def meth(x): ...
        class BadPG(te.Protocol[T]):
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

    def test_protocols_isinstance_py36(self):
        class Coordinate(te.Protocol):
            x: int
            y: int
        @te.runtime_checkable
        class Point(Coordinate, te.Protocol):
            label: str
        class XAxis(te.Protocol):
            x: int
        class YAxis(te.Protocol):
            y: int
        @te.runtime_checkable
        class Position(XAxis, YAxis, te.Protocol):
            pass
        @te.runtime_checkable
        class Proto(te.Protocol):
            attr: int
            def meth(self, arg: str) -> int: ...

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
        class MyPoint:
            x: int
            y: int
            label: str
        class Other:
            attr: int = 1
            def meth(self, arg: str) -> int:
                if arg == 'this':
                    return 1
                return 0
        class Concrete(Proto): pass
        class C:
            def __init__(self, attr):
                self.attr = attr
            def meth(self, arg):
                return 0
        class Bad: pass
        class NT(typing.NamedTuple):
            x: int
            y: int
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
        T = typing.TypeVar('T')
        @te.runtime_checkable
        class P(te.Protocol):
            x = 1
        @te.runtime_checkable
        class PG(te.Protocol[T]):
            x = 1
        class C:
            def __init__(self, x):
                self.x = x
        self.assertIsInstance(C(1), P)
        self.assertIsInstance(C(1), PG)

    def test_protocols_support_register(self):
        @te.runtime_checkable
        class P(te.Protocol):
            x = 1
        class PM(te.Protocol):
            def meth(self): pass
        class D(PM): pass
        class C: pass
        D.register(C)
        P.register(C)
        self.assertIsInstance(C(), P)
        self.assertIsInstance(C(), D)

    def test_none_on_non_callable_doesnt_block_implementation(self):
        @te.runtime_checkable
        class P(te.Protocol):
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
        @te.runtime_checkable
        class P(te.Protocol):
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
        class P(te.Protocol):
            x = 1
        @te.runtime_checkable
        class PR(te.Protocol):
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
        class P(te.Protocol):
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
        @te.runtime_checkable
        class P(te.Protocol):
            x = 1
        class C: pass
        with self.assertRaises(TypeError):
            issubclass(C(), P)

    def test_defining_generic_protocols_old_style(self):
        T = typing.TypeVar('T')
        S = typing.TypeVar('S')
        @te.runtime_checkable
        class PR(te.Protocol, typing.Generic[T, S]):
            def meth(self): pass
        class P(PR[int, str], te.Protocol):
            y = 1
        with self.assertRaises(TypeError):
            self.assertIsSubclass(PR[int, str], PR)
        self.assertIsSubclass(P, PR)
        with self.assertRaises(TypeError):
            PR[int]
        if not TYPING_3_10_0:
            with self.assertRaises(TypeError):
                PR[int, 1]
        class P1(te.Protocol, typing.Generic[T]):
            def bar(self, x: T) -> str: ...
        class P2(typing.Generic[T], te.Protocol):
            def bar(self, x: T) -> str: ...
        @te.runtime_checkable
        class PSub(P1[str], te.Protocol):
            x = 1
        class Test:
            x = 1
            def bar(self, x: str) -> str:
                return x
        self.assertIsInstance(Test(), PSub)
        if not TYPING_3_10_0:
            with self.assertRaises(TypeError):
                PR[int, typing.ClassVar]

    def test_init_called(self):
        T = typing.TypeVar('T')
        class P(te.Protocol[T]): pass
        class C(P[T]):
            def __init__(self):
                self.test = 'OK'
        self.assertEqual(C[int]().test, 'OK')

    def test_protocols_bad_subscripts(self):
        T = typing.TypeVar('T')
        S = typing.TypeVar('S')
        with self.assertRaises(TypeError):
            class P(te.Protocol[T, T]): pass
        with self.assertRaises(TypeError):
            class P(te.Protocol[int]): pass
        with self.assertRaises(TypeError):
            class P(te.Protocol[T], te.Protocol[S]): pass
        with self.assertRaises(TypeError):
            class P(typing.Mapping[T, S], te.Protocol[T]): pass

    def test_generic_protocols_repr(self):
        T = typing.TypeVar('T')
        S = typing.TypeVar('S')
        class P(te.Protocol[T, S]): pass
        self.assertTrue(repr(P[T, S]).endswith('P[~T, ~S]'))
        self.assertTrue(repr(P[int, str]).endswith('P[int, str]'))

    def test_generic_protocols_eq(self):
        T = typing.TypeVar('T')
        S = typing.TypeVar('S')
        class P(te.Protocol[T, S]): pass
        self.assertEqual(P, P)
        self.assertEqual(P[int, T], P[int, T])
        self.assertEqual(P[T, T][typing.Tuple[T, S]][int, str],
                         P[typing.Tuple[int, str], typing.Tuple[int, str]])

    def test_generic_protocols_special_from_protocol(self):
        @te.runtime_checkable
        class PR(te.Protocol):
            x = 1
        class P(te.Protocol):
            def meth(self):
                pass
        T = typing.TypeVar('T')
        class PG(te.Protocol[T]):
            x = 1
            def meth(self):
                pass
        self.assertTrue(P._is_protocol)
        self.assertTrue(PR._is_protocol)
        self.assertTrue(PG._is_protocol)
        if hasattr(typing, 'Protocol'):
            self.assertFalse(P._is_runtime_protocol)
        else:
            with self.assertRaises(AttributeError):
                self.assertFalse(P._is_runtime_protocol)
        self.assertTrue(PR._is_runtime_protocol)
        self.assertTrue(PG[int]._is_protocol)
        self.assertEqual(_get_protocol_attrs(P), {'meth'})
        self.assertEqual(_get_protocol_attrs(PR), {'x'})
        self.assertEqual(frozenset(_get_protocol_attrs(PG)),
                         frozenset({'x', 'meth'}))

    def test_no_runtime_deco_on_nominal(self):
        with self.assertRaises(TypeError):
            @te.runtime_checkable
            class C: pass
        class Proto(te.Protocol):
            x = 1
        with self.assertRaises(TypeError):
            @te.runtime_checkable
            class Concrete(Proto):
                pass

    def test_none_treated_correctly(self):
        @te.runtime_checkable
        class P(te.Protocol):
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
        class P(te.Protocol):
            x = None  # type: int
        Alias = typing.Union[typing.Iterable, P]
        Alias2 = typing.Union[P, typing.Iterable]
        self.assertEqual(Alias, Alias2)

    def test_protocols_pickleable(self):
        global P, CP  # pickle wants to reference the class by name
        T = typing.TypeVar('T')

        @te.runtime_checkable
        class P(te.Protocol[T]):
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

    def test_collections_protocols_allowed(self):
        @te.runtime_checkable
        class Custom(collections.abc.Iterable, te.Protocol):
            def close(self): pass

        class A: ...
        class B:
            def __iter__(self):
                return []
            def close(self):
                return 0

        self.assertIsSubclass(B, Custom)
        self.assertNotIsSubclass(A, Custom)

    def test_no_init_same_for_different_protocol_implementations(self):
        class CustomProtocolWithoutInitA(te.Protocol):
            pass

        class CustomProtocolWithoutInitB(te.Protocol):
            pass

        self.assertEqual(CustomProtocolWithoutInitA.__init__, CustomProtocolWithoutInitB.__init__)


class TypedDictTests(BaseTestCase):

    def test_basics_iterable_syntax(self):
        Emp = te.TypedDict('Emp', {'name': str, 'id': int})
        self.assertIsSubclass(Emp, dict)
        self.assertIsSubclass(Emp, typing.MutableMapping)
        self.assertNotIsSubclass(Emp, collections.abc.Sequence)
        jim = Emp(name='Jim', id=1)
        self.assertIs(type(jim), dict)
        self.assertEqual(jim['name'], 'Jim')
        self.assertEqual(jim['id'], 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__module__, __name__)
        self.assertEqual(Emp.__bases__, (dict,))
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})
        self.assertEqual(Emp.__total__, True)

    def test_basics_keywords_syntax(self):
        Emp = te.TypedDict('Emp', name=str, id=int)
        self.assertIsSubclass(Emp, dict)
        self.assertIsSubclass(Emp, typing.MutableMapping)
        self.assertNotIsSubclass(Emp, collections.abc.Sequence)
        jim = Emp(name='Jim', id=1)
        self.assertIs(type(jim), dict)
        self.assertEqual(jim['name'], 'Jim')
        self.assertEqual(jim['id'], 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__module__, __name__)
        self.assertEqual(Emp.__bases__, (dict,))
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})
        self.assertEqual(Emp.__total__, True)

    def test_typeddict_special_keyword_names(self):
        TD = te.TypedDict("TD", cls=type, self=object, typename=str, _typename=int,
                          fields=list, _fields=dict)
        self.assertEqual(TD.__name__, 'TD')
        self.assertEqual(TD.__annotations__, {'cls': type, 'self': object, 'typename': str,
                                              '_typename': int, 'fields': list, '_fields': dict})
        a = TD(cls=str, self=42, typename='foo', _typename=53,
               fields=[('bar', tuple)], _fields={'baz', set})
        self.assertEqual(a['cls'], str)
        self.assertEqual(a['self'], 42)
        self.assertEqual(a['typename'], 'foo')
        self.assertEqual(a['_typename'], 53)
        self.assertEqual(a['fields'], [('bar', tuple)])
        self.assertEqual(a['_fields'], {'baz', set})

    @skipIf(hasattr(typing, 'TypedDict'), "Should be tested by upstream")
    def test_typeddict_create_errors(self):
        with self.assertRaises(TypeError):
            te.TypedDict.__new__()
        with self.assertRaises(TypeError):
            te.TypedDict()
        with self.assertRaises(TypeError):
            te.TypedDict('Emp', [('name', str)], None)

        with self.assertWarns(DeprecationWarning):
            Emp = te.TypedDict(_typename='Emp', name=str, id=int)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})

        with self.assertWarns(DeprecationWarning):
            Emp = te.TypedDict('Emp', _fields={'name': str, 'id': int})
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})

    def test_typeddict_errors(self):
        Emp = te.TypedDict('Emp', {'name': str, 'id': int})
        if sys.version_info >= (3, 9, 2):
            self.assertEqual(te.TypedDict.__module__, 'typing')
        else:
            self.assertEqual(te.TypedDict.__module__, 'typing_extensions')
        jim = Emp(name='Jim', id=1)
        with self.assertRaises(TypeError):
            isinstance({}, Emp)
        with self.assertRaises(TypeError):
            isinstance(jim, Emp)
        with self.assertRaises(TypeError):
            issubclass(dict, Emp)
        with self.assertRaises(TypeError):
            te.TypedDict('Hi', x=1)
        with self.assertRaises(TypeError):
            te.TypedDict('Hi', [('x', int), ('y', 1)])
        with self.assertRaises(TypeError):
            te.TypedDict('Hi', [('x', int)], y=int)

    def test_py36_class_syntax_usage(self):
        class Point2D(te.TypedDict):
            x: int
            y: int
        Label = te.TypedDict('Label', [('label', str)])
        class LabelPoint2D(Point2D, Label): ...
        self.assertEqual(LabelPoint2D.__name__, 'LabelPoint2D')
        self.assertEqual(LabelPoint2D.__module__, __name__)
        self.assertEqual(gth(LabelPoint2D), {'x': int, 'y': int, 'label': str})
        self.assertEqual(LabelPoint2D.__bases__, (dict,))
        self.assertEqual(LabelPoint2D.__total__, True)
        self.assertNotIsSubclass(LabelPoint2D, typing.Sequence)
        not_origin = Point2D(x=0, y=1)
        self.assertEqual(not_origin['x'], 0)
        self.assertEqual(not_origin['y'], 1)
        other = LabelPoint2D(x=0, y=1, label='hi')
        self.assertEqual(other['label'], 'hi')

    def test_pickle(self):
        global EmpD  # pickle wants to reference the class by name
        EmpD = te.TypedDict('EmpD', name=str, id=int)
        jane = EmpD({'name': 'jane', 'id': 37})
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(jane, proto)
            jane2 = pickle.loads(z)
            self.assertEqual(jane2, jane)
            self.assertEqual(jane2, {'name': 'jane', 'id': 37})
            ZZ = pickle.dumps(EmpD, proto)
            EmpDnew = pickle.loads(ZZ)
            self.assertEqual(EmpDnew({'name': 'jane', 'id': 37}), jane)

    def test_optional(self):
        EmpD = te.TypedDict('EmpD', name=str, id=int)

        self.assertEqual(typing.Optional[EmpD], typing.Union[None, EmpD])
        self.assertNotEqual(typing.List[EmpD], typing.Tuple[EmpD])

    def test_total(self):
        D = te.TypedDict('D', {'x': int}, total=False)
        self.assertEqual(D(), {})
        self.assertEqual(D(x=1), {'x': 1})
        self.assertEqual(D.__total__, False)
        self.assertEqual(D.__required_keys__, frozenset())
        self.assertEqual(D.__optional_keys__, {'x'})

        class Options(te.TypedDict, total=False):
            log_level: int
            log_path: str
        self.assertEqual(Options(), {})
        self.assertEqual(Options(log_level=2), {'log_level': 2})
        self.assertEqual(Options.__total__, False)
        self.assertEqual(Options.__required_keys__, frozenset())
        self.assertEqual(Options.__optional_keys__, {'log_level', 'log_path'})

    def test_optional_keys(self):
        class Point2D(te.TypedDict):
            x: int
            y: int
        class Point2Dor3D(Point2D, total=False):
            z: int
        assert Point2Dor3D.__required_keys__ == frozenset(['x', 'y'])
        assert Point2Dor3D.__optional_keys__ == frozenset(['z'])

    def test_keys_inheritance(self):
        class BaseAnimal(te.TypedDict):
            name: str

        class Animal(BaseAnimal, total=False):
            voice: str
            tail: bool

        class Cat(Animal):
            fur_color: str

        assert BaseAnimal.__required_keys__ == frozenset(['name'])
        assert BaseAnimal.__optional_keys__ == frozenset([])
        assert gth(BaseAnimal) == {'name': str}

        assert Animal.__required_keys__ == frozenset(['name'])
        assert Animal.__optional_keys__ == frozenset(['tail', 'voice'])
        assert gth(Animal) == {
            'name': str,
            'tail': bool,
            'voice': str,
        }

        assert Cat.__required_keys__ == frozenset(['name', 'fur_color'])
        assert Cat.__optional_keys__ == frozenset(['tail', 'voice'])
        assert gth(Cat) == {
            'fur_color': str,
            'name': str,
            'tail': bool,
            'voice': str,
        }


class AnnotatedTests(BaseTestCase):

    def test_repr(self):
        if hasattr(typing, 'Annotated'):
            mod_name = 'typing'
        else:
            mod_name = "typing_extensions"
        self.assertEqual(
            repr(te.Annotated[int, 4, 5]),
            mod_name + ".Annotated[int, 4, 5]"
        )
        self.assertEqual(
            repr(te.Annotated[typing.List[int], 4, 5]),
            mod_name + ".Annotated[typing.List[int], 4, 5]"
        )

    def test_flatten(self):
        A = te.Annotated[te.Annotated[int, 4], 5]
        self.assertEqual(A, te.Annotated[int, 4, 5])
        self.assertEqual(A.__metadata__, (4, 5))
        self.assertEqual(A.__origin__, int)

    def test_specialize(self):
        L = te.Annotated[typing.List[T], "my decoration"]
        LI = te.Annotated[typing.List[int], "my decoration"]
        self.assertEqual(L[int], te.Annotated[typing.List[int], "my decoration"])
        self.assertEqual(L[int].__metadata__, ("my decoration",))
        self.assertEqual(L[int].__origin__, typing.List[int])
        with self.assertRaises(TypeError):
            LI[int]
        with self.assertRaises(TypeError):
            L[int, float]

    def test_hash_eq(self):
        self.assertEqual(len({te.Annotated[int, 4, 5], te.Annotated[int, 4, 5]}), 1)
        self.assertNotEqual(te.Annotated[int, 4, 5], te.Annotated[int, 5, 4])
        self.assertNotEqual(te.Annotated[int, 4, 5], te.Annotated[str, 4, 5])
        self.assertNotEqual(te.Annotated[int, 4], te.Annotated[int, 4, 4])
        self.assertEqual(
            {te.Annotated[int, 4, 5], te.Annotated[int, 4, 5], te.Annotated[T, 4, 5]},
            {te.Annotated[int, 4, 5], te.Annotated[T, 4, 5]}
        )

    def test_instantiate(self):
        class C:
            classvar = 4

            def __init__(self, x):
                self.x = x

            def __eq__(self, other):
                if not isinstance(other, C):
                    return NotImplemented
                return other.x == self.x

        A = te.Annotated[C, "a decoration"]
        a = A(5)
        c = C(5)
        self.assertEqual(a, c)
        self.assertEqual(a.x, c.x)
        self.assertEqual(a.classvar, c.classvar)

    def test_instantiate_generic(self):
        MyCount = te.Annotated[typing.Counter[T], "my decoration"]
        self.assertEqual(MyCount([4, 4, 5]), {4: 2, 5: 1})
        self.assertEqual(MyCount[int]([4, 4, 5]), {4: 2, 5: 1})

    def test_cannot_instantiate_forward(self):
        A = te.Annotated["int", (5, 6)]
        with self.assertRaises(TypeError):
            A(5)

    def test_cannot_instantiate_type_var(self):
        A = te.Annotated[T, (5, 6)]
        with self.assertRaises(TypeError):
            A(5)

    def test_cannot_getattr_typevar(self):
        with self.assertRaises(AttributeError):
            te.Annotated[T, (5, 7)].x

    def test_attr_passthrough(self):
        class C:
            classvar = 4

        A = te.Annotated[C, "a decoration"]
        self.assertEqual(A.classvar, 4)
        A.x = 5
        self.assertEqual(C.x, 5)

    def test_hash_eq(self):
        self.assertEqual(len({te.Annotated[int, 4, 5], te.Annotated[int, 4, 5]}), 1)
        self.assertNotEqual(te.Annotated[int, 4, 5], te.Annotated[int, 5, 4])
        self.assertNotEqual(te.Annotated[int, 4, 5], te.Annotated[str, 4, 5])
        self.assertNotEqual(te.Annotated[int, 4], te.Annotated[int, 4, 4])
        self.assertEqual(
            {te.Annotated[int, 4, 5], te.Annotated[int, 4, 5], te.Annotated[T, 4, 5]},
            {te.Annotated[int, 4, 5], te.Annotated[T, 4, 5]}
        )

    def test_cannot_subclass(self):
        with self.assertRaisesRegex(TypeError, "Cannot subclass .*Annotated"):
            class C(te.Annotated):
                pass

    def test_cannot_check_instance(self):
        with self.assertRaises(TypeError):
            isinstance(5, te.Annotated[int, "positive"])

    def test_cannot_check_subclass(self):
        with self.assertRaises(TypeError):
            issubclass(int, te.Annotated[int, "positive"])

    def test_pickle(self):
        samples = [typing.Any, typing.Union[int, str],
                   typing.Optional[str], typing.Tuple[int, ...],
                   typing.Callable[[str], bytes]]

        for t in samples:
            x = te.Annotated[t, "a"]

            for prot in range(pickle.HIGHEST_PROTOCOL + 1):
                with self.subTest(protocol=prot, type=t):
                    pickled = pickle.dumps(x, prot)
                    restored = pickle.loads(pickled)
                    self.assertEqual(x, restored)

        global _Annotated_test_G

        class _Annotated_test_G(typing.Generic[T]):
            x = 1

        G = te.Annotated[_Annotated_test_G[int], "A decoration"]
        G.foo = 42
        G.bar = 'abc'

        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(G, proto)
            x = pickle.loads(z)
            self.assertEqual(x.foo, 42)
            self.assertEqual(x.bar, 'abc')
            self.assertEqual(x.x, 1)

    def test_subst(self):
        dec = "a decoration"
        dec2 = "another decoration"

        S = te.Annotated[T, dec2]
        self.assertEqual(S[int], te.Annotated[int, dec2])

        self.assertEqual(S[te.Annotated[int, dec]], te.Annotated[int, dec, dec2])
        L = te.Annotated[typing.List[T], dec]

        self.assertEqual(L[int], te.Annotated[typing.List[int], dec])
        with self.assertRaises(TypeError):
            L[int, int]

        self.assertEqual(S[L[int]], te.Annotated[typing.List[int], dec, dec2])

        D = te.Annotated[typing.Dict[KT, VT], dec]
        self.assertEqual(D[str, int], te.Annotated[typing.Dict[str, int], dec])
        with self.assertRaises(TypeError):
            D[int]

        It = te.Annotated[int, dec]
        with self.assertRaises(TypeError):
            It[None]

        LI = L[int]
        with self.assertRaises(TypeError):
            LI[None]

    def test_annotated_in_other_types(self):
        X = typing.List[te.Annotated[T, 5]]
        self.assertEqual(X[int], typing.List[te.Annotated[int, 5]])


class GetTypeHintsTests(BaseTestCase):
    def test_get_type_hints_modules(self):
        ann_module_type_hints = {1: 2, 'f': typing.Tuple[int, int], 'x': int, 'y': str}
        if TYPING_3_10_0:
            ann_module_type_hints['u'] = int | float
        self.assertEqual(gth(ann_module), ann_module_type_hints)
        self.assertEqual(gth(ann_module2), {})
        self.assertEqual(gth(ann_module3), {})

    def test_get_type_hints_classes(self):
        class NoneAndForward:
            parent: 'NoneAndForward'
            meaning: None

        self.assertEqual(gth(ann_module.C, ann_module.__dict__),
                         {'y': typing.Optional[ann_module.C]})
        self.assertIsInstance(gth(ann_module.j_class), dict)
        self.assertEqual(gth(ann_module.M), {'123': 123, 'o': type})
        self.assertEqual(gth(ann_module.D),
                         {'j': str, 'k': str, 'y': typing.Optional[ann_module.C]})
        self.assertEqual(gth(ann_module.Y), {'z': int})
        self.assertEqual(gth(ann_module.h_class),
                         {'y': typing.Optional[ann_module.C]})
        self.assertEqual(gth(ann_module.S), {'x': str, 'y': str})
        self.assertEqual(gth(ann_module.foo), {'x': int})
        self.assertEqual(gth(NoneAndForward, locals()),
                         {'parent': NoneAndForward, 'meaning': type(None)})

    def test_get_type_hints_functions(self):
        def foobar(x: typing.List['X']): ...
        X = te.Annotated[int, (1, 10)]
        self.assertEqual(
            gth(foobar, globals(), locals()),
            {'x': typing.List[int]}
        )
        self.assertEqual(
            gth(foobar, globals(), locals(), include_extras=True),
            {'x': typing.List[te.Annotated[int, (1, 10)]]}
        )
        BA = typing.Tuple[te.Annotated[T, (1, 0)], ...]
        def barfoo(x: BA): ...
        self.assertEqual(gth(barfoo, globals(), locals())['x'], typing.Tuple[T, ...])
        self.assertIs(
            gth(barfoo, globals(), locals(), include_extras=True)['x'],
            BA
        )
        def barfoo2(x: typing.Callable[..., te.Annotated[typing.List[T], "const"]],
                    y: typing.Union[int, te.Annotated[T, "mutable"]]): ...
        self.assertEqual(
            gth(barfoo2, globals(), locals()),
            {'x': typing.Callable[..., typing.List[T]], 'y': typing.Union[int, T]}
        )
        BA2 = typing.Callable[..., typing.List[T]]
        def barfoo3(x: BA2): ...
        self.assertIs(
            gth(barfoo3, globals(), locals(), include_extras=True)["x"],
            BA2
        )

    def test_respect_no_type_check(self):
        @typing.no_type_check
        class NoTpCheck:
            class Inn:
                def __init__(self, x: 'not a type'): ...  # noqa
        self.assertTrue(NoTpCheck.__no_type_check__)
        self.assertTrue(NoTpCheck.Inn.__init__.__no_type_check__)
        self.assertEqual(gth(ann_module2.NTC.meth), {})
        class ABase(typing.Generic[T]):
            def meth(x: int): ...
        @typing.no_type_check
        class Der(ABase): ...
        self.assertEqual(gth(ABase.meth), {'x': int})

    def test_final_forward_ref(self):
        class Loop:
            attr: te.Final['Loop']
        self.assertEqual(gth(Loop, locals())['attr'], te.Final[Loop])
        self.assertNotEqual(gth(Loop, locals())['attr'], te.Final[int])
        self.assertNotEqual(gth(Loop, locals())['attr'], te.Final)

    def test_get_type_hints_refs(self):

        Const = te.Annotated[T, "Const"]

        class MySet(typing.Generic[T]):

            def __ior__(self, other: "Const[MySet[T]]") -> "MySet[T]":
                ...

            def __iand__(self, other: Const["MySet[T]"]) -> "MySet[T]":
                ...

        self.assertEqual(
            gth(MySet.__iand__, globals(), locals()),
            {'other': MySet[T], 'return': MySet[T]}
        )

        self.assertEqual(
            gth(MySet.__iand__, globals(), locals(), include_extras=True),
            {'other': Const[MySet[T]], 'return': MySet[T]}
        )

        self.assertEqual(
            gth(MySet.__ior__, globals(), locals()),
            {'other': MySet[T], 'return': MySet[T]}
        )


class TypeAliasTests(BaseTestCase):
    def test_canonical_usage_with_variable_annotation(self):
        Alias: te.TypeAlias = Employee

    def test_canonical_usage_with_type_comment(self):
        Alias = Employee  # type: TypeAlias

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            te.TypeAlias()

    def test_no_isinstance(self):
        with self.assertRaises(TypeError):
            isinstance(42, te.TypeAlias)

    def test_no_issubclass(self):
        with self.assertRaises(TypeError):
            issubclass(Employee, te.TypeAlias)

        with self.assertRaises(TypeError):
            issubclass(te.TypeAlias, Employee)

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class C(te.TypeAlias):
                pass

        with self.assertRaises(TypeError):
            class C(type(te.TypeAlias)):
                pass

    def test_repr(self):
        if hasattr(typing, 'TypeAlias'):
            self.assertEqual(repr(te.TypeAlias), 'typing.TypeAlias')
        else:
            self.assertEqual(repr(te.TypeAlias), 'typing_extensions.TypeAlias')

    def test_cannot_subscript(self):
        with self.assertRaises(TypeError):
            te.TypeAlias[int]


class ParamSpecTests(BaseTestCase):

    def test_basic_plain(self):
        P = te.ParamSpec('P')
        self.assertEqual(P, P)
        self.assertIsInstance(P, te.ParamSpec)
        # Should be hashable
        hash(P)

    def test_repr(self):
        P = te.ParamSpec('P')
        P_co = te.ParamSpec('P_co', covariant=True)
        P_contra = te.ParamSpec('P_contra', contravariant=True)
        P_2 = te.ParamSpec('P_2')
        self.assertEqual(repr(P), '~P')
        self.assertEqual(repr(P_2), '~P_2')

        # Note: PEP 612 doesn't require these to be repr-ed correctly, but
        # just follow CPython.
        self.assertEqual(repr(P_co), '+P_co')
        self.assertEqual(repr(P_contra), '-P_contra')

    def test_valid_uses(self):
        P = te.ParamSpec('P')
        T = typing.TypeVar('T')
        C1 = typing.Callable[P, int]
        self.assertEqual(C1.__args__, (P, int))
        self.assertEqual(C1.__parameters__, (P,))
        C2 = typing.Callable[P, T]
        self.assertEqual(C2.__args__, (P, T))
        self.assertEqual(C2.__parameters__, (P, T))


        # Test collections.abc.Callable too.
        if sys.version_info[:2] >= (3, 9):
            # Note: no tests for Callable.__parameters__ here
            # because types.GenericAlias Callable is hardcoded to search
            # for tp_name "TypeVar" in C.  This was changed in 3.10.
            C3 = collections.abc.Callable[P, int]
            self.assertEqual(C3.__args__, (P, int))
            C4 = collections.abc.Callable[P, T]
            self.assertEqual(C4.__args__, (P, T))

        # ParamSpec instances should also have args and kwargs attributes.
        # Note: not in dir(P) because of __class__ hacks
        self.assertTrue(hasattr(P, 'args'))
        self.assertTrue(hasattr(P, 'kwargs'))

    def test_args_kwargs(self):
        P = te.ParamSpec('P')
        # Note: not in dir(P) because of __class__ hacks
        self.assertTrue(hasattr(P, 'args'))
        self.assertTrue(hasattr(P, 'kwargs'))
        self.assertIsInstance(P.args, te.ParamSpecArgs)
        self.assertIsInstance(P.kwargs, te.ParamSpecKwargs)
        self.assertIs(P.args.__origin__, P)
        self.assertIs(P.kwargs.__origin__, P)
        self.assertEqual(repr(P.args), "P.args")
        self.assertEqual(repr(P.kwargs), "P.kwargs")

    def test_user_generics(self):
        T = typing.TypeVar("T")
        P = te.ParamSpec("P")
        P_2 = te.ParamSpec("P_2")

        class X(typing.Generic[T, P]):
            pass

        G1 = X[int, P_2]
        self.assertEqual(G1.__args__, (int, P_2))
        self.assertEqual(G1.__parameters__, (P_2,))

        G2 = X[int, te.Concatenate[int, P_2]]
        self.assertEqual(G2.__args__, (int, te.Concatenate[int, P_2]))
        self.assertEqual(G2.__parameters__, (P_2,))

        # The following are some valid uses cases in PEP 612 that don't work:
        # These do not work in 3.9, _type_check blocks the list and ellipsis.
        # G3 = X[int, [int, bool]]
        # G4 = X[int, ...]
        # G5 = Z[[int, str, bool]]
        # Not working because this is special-cased in 3.10.
        # G6 = Z[int, str, bool]

        class Z(typing.Generic[P]):
            pass

    def test_pickle(self):
        global P, P_co, P_contra
        P = te.ParamSpec('P')
        P_co = te.ParamSpec('P_co', covariant=True)
        P_contra = te.ParamSpec('P_contra', contravariant=True)
        for proto in range(pickle.HIGHEST_PROTOCOL):
            with self.subTest(f'Pickle protocol {proto}'):
                for paramspec in (P, P_co, P_contra):
                    z = pickle.loads(pickle.dumps(paramspec, proto))
                    self.assertEqual(z.__name__, paramspec.__name__)
                    self.assertEqual(z.__covariant__, paramspec.__covariant__)
                    self.assertEqual(z.__contravariant__, paramspec.__contravariant__)
                    self.assertEqual(z.__bound__, paramspec.__bound__)

    def test_eq(self):
        P = te.ParamSpec('P')
        self.assertEqual(P, P)
        self.assertEqual(hash(P), hash(P))
        # ParamSpec should compare by id similar to TypeVar in CPython
        self.assertNotEqual(te.ParamSpec('P'), P)
        self.assertIsNot(te.ParamSpec('P'), P)
        # Note: normally you don't test this as it breaks when there's
        # a hash collision. However, ParamSpec *must* guarantee that
        # as long as two objects don't have the same ID, their hashes
        # won't be the same.
        self.assertNotEqual(hash(te.ParamSpec('P')), hash(P))


class ConcatenateTests(BaseTestCase):
    def test_basics(self):
        P = te.ParamSpec('P')

        class MyClass: ...

        c = te.Concatenate[MyClass, P]
        self.assertNotEqual(c, te.Concatenate)

    def test_valid_uses(self):
        P = te.ParamSpec('P')
        T = typing.TypeVar('T')
        C1 = typing.Callable[te.Concatenate[int, P], int]
        C2 = typing.Callable[te.Concatenate[int, T, P], T]

        # Test collections.abc.Callable too.
        if sys.version_info[:2] >= (3, 9):
            C3 = collections.abc.Callable[te.Concatenate[int, P], int]
            C4 = collections.abc.Callable[te.Concatenate[int, T, P], T]

    def test_basic_introspection(self):
        P = te.ParamSpec('P')
        C1 = te.Concatenate[int, P]
        C2 = te.Concatenate[int, T, P]
        self.assertEqual(C1.__origin__, te.Concatenate)
        self.assertEqual(C1.__args__, (int, P))
        self.assertEqual(C2.__origin__, te.Concatenate)
        self.assertEqual(C2.__args__, (int, T, P))

    def test_eq(self):
        P = te.ParamSpec('P')
        C1 = te.Concatenate[int, P]
        C2 = te.Concatenate[int, P]
        C3 = te.Concatenate[int, T, P]
        self.assertEqual(C1, C2)
        self.assertEqual(hash(C1), hash(C2))
        self.assertNotEqual(C1, C3)


class TypeGuardTests(BaseTestCase):
    def test_basics(self):
        te.TypeGuard[int]  # OK
        self.assertEqual(te.TypeGuard[int], te.TypeGuard[int])

        def foo(arg) -> te.TypeGuard[int]: ...
        self.assertEqual(gth(foo), {'return': te.TypeGuard[int]})

    def test_repr(self):
        if hasattr(typing, 'TypeGuard'):
            mod_name = 'typing'
        else:
            mod_name = 'typing_extensions'
        self.assertEqual(repr(te.TypeGuard), f'{mod_name}.TypeGuard')
        cv = te.TypeGuard[int]
        self.assertEqual(repr(cv), f'{mod_name}.TypeGuard[int]')
        cv = te.TypeGuard[Employee]
        self.assertEqual(repr(cv), f'{mod_name}.TypeGuard[{__name__}.Employee]')
        cv = te.TypeGuard[typing.Tuple[int]]
        self.assertEqual(repr(cv), f'{mod_name}.TypeGuard[typing.Tuple[int]]')

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class C(type(te.TypeGuard)):
                pass
        with self.assertRaises(TypeError):
            class C(type(te.TypeGuard[int])):
                pass

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            te.TypeGuard()
        with self.assertRaises(TypeError):
            type(te.TypeGuard)()
        with self.assertRaises(TypeError):
            type(te.TypeGuard[typing.Optional[int]])()

    def test_no_isinstance(self):
        with self.assertRaises(TypeError):
            isinstance(1, te.TypeGuard[int])
        with self.assertRaises(TypeError):
            issubclass(int, te.TypeGuard)


class SelfTests(BaseTestCase):
    def test_basics(self):
        class Foo:
            def bar(self) -> te.Self: ...

        self.assertEqual(gth(Foo.bar), {'return': te.Self})

    def test_repr(self):
        if hasattr(typing, 'Self'):
            mod_name = 'typing'
        else:
            mod_name = 'typing_extensions'
        self.assertEqual(repr(te.Self), '{}.Self'.format(mod_name))

    def test_cannot_subscript(self):
        with self.assertRaises(TypeError):
            te.Self[int]

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class C(type(te.Self)):
                pass

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            te.Self()
        with self.assertRaises(TypeError):
            type(te.Self)()

    def test_no_isinstance(self):
        with self.assertRaises(TypeError):
            isinstance(1, te.Self)
        with self.assertRaises(TypeError):
            issubclass(int, te.Self)

    def test_alias(self):
        TupleSelf = typing.Tuple[te.Self, te.Self]
        class Alias:
            def return_tuple(self) -> TupleSelf:
                return (self, self)

class AllTests(BaseTestCase):

    def test_typing_extensions_includes_standard(self):
        a = te.__all__
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
        self.assertIn('TypeAlias', a)
        self.assertIn('ParamSpec', a)
        self.assertIn("Concatenate", a)

        self.assertIn('Annotated', a)
        self.assertIn('get_type_hints', a)

        self.assertIn('Awaitable', a)
        self.assertIn('AsyncIterator', a)
        self.assertIn('AsyncIterable', a)
        self.assertIn('Coroutine', a)
        self.assertIn('AsyncContextManager', a)

        self.assertIn('AsyncGenerator', a)

        self.assertIn('Protocol', a)
        self.assertIn('runtime', a)

        # Check that all objects in `__all__` are present in the module
        for name in a:
            self.assertTrue(hasattr(te, name))

    def test_typing_extensions_defers_when_possible(self):
        exclude = {
            'overload',
            'Text',
            'TypedDict',
            'TYPE_CHECKING',
            'Final',
            'get_type_hints'
        }
        if sys.version_info < (3, 10):
            exclude |= {'get_args', 'get_origin'}
        for item in te.__all__:
            if item not in exclude and hasattr(typing, item):
                self.assertIs(
                    getattr(te, item),
                    getattr(typing, item))

    def test_typing_extensions_compiles_with_opt(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'typing_extensions.py')
        try:
            subprocess.check_output(f'{sys.executable} -OO {file_path}',
                                    stderr=subprocess.STDOUT,
                                    shell=True)
        except subprocess.CalledProcessError:
            self.fail('Module does not compile with optimize=2 (-OO flag).')


if __name__ == '__main__':
    main()
