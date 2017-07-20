import sys
import os
import abc
import contextlib
import collections
from unittest import TestCase, main, skipUnless

from typing_extensions import NoReturn, ClassVar
from typing_extensions import ContextManager, Counter, Deque, DefaultDict
from typing_extensions import NewType, overload
import typing
import typing_extensions


T = typing.TypeVar('T')
KT = typing.TypeVar('KT')
VT = typing.TypeVar('VT')


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


class Employee(object):
    pass


class NoReturnTests(BaseTestCase):

    def test_noreturn_instance_type_error(self):
        with self.assertRaises(TypeError):
            isinstance(42, NoReturn)

    def test_noreturn_subclass_type_error(self):
        with self.assertRaises(TypeError):
            issubclass(Employee, NoReturn)
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
        self.assertEqual(repr(ClassVar), 'typing.ClassVar')
        cv = ClassVar[int]
        self.assertEqual(repr(cv), 'typing.ClassVar[int]')
        cv = ClassVar[Employee]
        self.assertEqual(repr(cv), 'typing.ClassVar[%s.Employee]' % __name__)

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
            type(ClassVar[typing.Optional[int]])()

    def test_no_isinstance(self):
        with self.assertRaises(TypeError):
            isinstance(1, ClassVar[int])
        with self.assertRaises(TypeError):
            issubclass(int, ClassVar)


class CollectionsAbcTests(BaseTestCase):

    def test_contextmanager(self):
        @contextlib.contextmanager
        def manager():
            yield 42

        cm = manager()
        self.assertIsInstance(cm, ContextManager)
        self.assertNotIsInstance(42, ContextManager)

        with self.assertRaises(TypeError):
            isinstance(42, ContextManager[int])
        with self.assertRaises(TypeError):
            isinstance(cm, ContextManager[int])
        with self.assertRaises(TypeError):
            issubclass(type(cm), ContextManager[int])

    def test_counter(self):
        self.assertIsSubclass(collections.Counter, Counter)
        self.assertIs(type(Counter()), collections.Counter)
        self.assertIs(type(Counter[T]()), collections.Counter)
        self.assertIs(type(Counter[int]()), collections.Counter)

        class A(Counter[int]): pass
        class B(Counter[T]): pass

        self.assertIsInstance(A(), collections.Counter)
        self.assertIs(type(B[int]()), B)
        self.assertEqual(B.__bases__, (typing_extensions.Counter,))

    def test_deque(self):
        self.assertIsSubclass(collections.deque, Deque)
        self.assertIs(type(Deque()), collections.deque)
        self.assertIs(type(Deque[T]()), collections.deque)
        self.assertIs(type(Deque[int]()), collections.deque)

        class A(Deque[int]): pass
        class B(Deque[T]): pass

        self.assertIsInstance(A(), collections.deque)
        self.assertIs(type(B[int]()), B)

    def test_defaultdict_instantiation(self):
        self.assertIsSubclass(collections.defaultdict, DefaultDict)
        self.assertIs(type(DefaultDict()), collections.defaultdict)
        self.assertIs(type(DefaultDict[KT, VT]()), collections.defaultdict)
        self.assertIs(type(DefaultDict[str, int]()), collections.defaultdict)

        class A(DefaultDict[str, int]): pass
        class B(DefaultDict[KT, VT]): pass

        self.assertIsInstance(A(), collections.defaultdict)
        self.assertIs(type(B[str, int]()), B)


class NewTypeTests(BaseTestCase):

    def test_basic(self):
        UserId = NewType('UserId', int)
        UserName = NewType('UserName', str)
        self.assertIsInstance(UserId(5), int)
        self.assertIsInstance(UserName('Joe'), type('Joe'))
        self.assertEqual(UserId(5) + 1, 6)

    def test_errors(self):
        UserId = NewType('UserId', int)
        UserName = NewType('UserName', str)
        with self.assertRaises(TypeError):
            issubclass(UserId, int)
        with self.assertRaises(TypeError):
            class D(UserName):
                pass


class OverloadTests(BaseTestCase):

    def test_overload_fails(self):
        with self.assertRaises(RuntimeError):
            @overload
            def blah():
                pass

            blah()

    def test_overload_succeeds(self):
        @overload
        def blah():
            pass

        def blah():
            pass

        blah()


class AllTests(BaseTestCase):

    def test_typing_extensions_includes_standard(self):
        a = typing_extensions.__all__
        self.assertIn('ClassVar', a)
        self.assertIn('Type', a)
        self.assertIn('Counter', a)
        self.assertIn('DefaultDict', a)
        self.assertIn('Deque', a)
        self.assertIn('NewType', a)
        self.assertIn('overload', a)
        self.assertIn('Text', a)
        self.assertIn('TYPE_CHECKING', a)

    def test_typing_extensions_defers_when_possible(self):
        exclude = {'overload', 'Text', 'TYPE_CHECKING'}
        for item in typing_extensions.__all__:
            if item not in exclude and hasattr(typing, item):
                self.assertIs(
                    getattr(typing_extensions, item),
                    getattr(typing, item))


if __name__ == '__main__':
    main()
