# Override version info
import sys
ORIGINAL_VERSION = sys.version_info
if len(sys.argv) >= 2:
    PYTHON_VERSION = tuple(map(int, sys.argv[1].split('.')))
    sys.version_info = PYTHON_VERSION
    OVERRIDING_VERSION = True
else:
    PYTHON_VERSION = ORIGINAL_VERSION
    OVERRIDING_VERSION = False

import os
import abc
import contextlib
import collections
from unittest import TestCase, main, skipUnless, SkipTest

from typing_extensions import NoReturn, ClassVar, Type, NewType
import typing
import typing_extensions


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

    def clear_caches(self):
        for f in typing._cleanups:
            f()


class EnvironmentTest(BaseTestCase):
    @skipUnless(OVERRIDING_VERSION, "Environment tests apply only when overriding")
    def test_environment_is_ok(self):
        cwd = os.path.abspath(os.getcwd())
        def correct_dir(module):
            return os.path.abspath(module.__file__).startswith(cwd)

        self.assertTrue(correct_dir(abc))
        self.assertTrue(correct_dir(collections))
        self.assertTrue(correct_dir(typing_extensions))

    def test_python_version_is_ok(self):
        self.assertTrue(sys.version_info == PYTHON_VERSION)
        self.assertTrue(ORIGINAL_VERSION[0] == 2)


class Employee:
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


class CollectionsAbcTests(BaseTestCase):

    def test_collection(self):
        self.assertIsInstance(tuple(), typing_extensions.Collection)
        self.assertIsInstance(frozenset(), typing_extensions.Collection)
        self.assertIsSubclass(dict, typing_extensions.Collection)
        self.assertNotIsInstance(42, typing_extensions.Collection)

    def test_collection_instantiation(self):
        class MyAbstractCollection(typing_extensions.Collection[int]): 
            pass
        class MyCollection(typing_extensions.Collection[int]):
            def __contains__(self, item): pass
            def __iter__(self): pass
            def __len__(self): pass

        self.assertIsSubclass(
                type(MyCollection()),
                typing_extensions.Collection)
        self.assertIsSubclass(
                MyCollection,
                typing_extensions.Collection)
        with self.assertRaises(TypeError):
            MyAbstractCollection()

    def test_contextmanager(self):
        @contextlib.contextmanager
        def manager():
            yield 42

        cm = manager()
        self.assertIsInstance(cm, typing_extensions.ContextManager)
        self.assertNotIsInstance(42, typing_extensions.ContextManager)


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

        self.assertIn('Collection', a)

    def test_typing_extensions_defers_when_possible(self):
        exclude = {'overload', 'Text', 'TYPE_CHECKING'}
        for item in typing_extensions.__all__:
            if item not in exclude and hasattr(typing, item):
                self.assertIs(
                        getattr(typing_extensions, item),
                        getattr(typing, item))

if __name__ == '__main__':
    main(argv=[sys.argv[0]] + sys.argv[2:])
