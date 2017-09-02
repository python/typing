import abc
import sys
import typing
from typing import (
    ClassVar, Type, Generic, Callable, GenericMeta, TypingMeta,
    Counter, DefaultDict, Deque, TypeVar, Tuple,
    NewType, overload, Text, TYPE_CHECKING,
    # We use internal typing helpers here, but this significantly reduces
    # code duplication. (Also this is only until Protocol is in typing.)
    _generic_new, _type_vars, _next_in_mro, _tp_cache, _type_check,
    _TypingEllipsis, _TypingEmpty, _check_generic
)

# Please keep __all__ alphabetized within each category.
__all__ = [
    # Super-special typing primitives.
    'ClassVar',
    'Type',
    'Protocol',

    # Concrete collection types.
    'ContextManager',
    'Counter',
    'Deque',
    'DefaultDict',

    # One-off things.
    'NewType',
    'overload',
    'runtime',
    'Text',
    'TYPE_CHECKING',
]


if hasattr(typing, 'NoReturn'):
    NoReturn = typing.NoReturn
else:
    # TODO: Remove once typing.py has been updated
    class NoReturnMeta(typing.TypingMeta):
        """Metaclass for NoReturn."""

        def __new__(cls, name, bases, namespace):
            cls.assert_no_subclassing(bases)
            self = super(NoReturnMeta, cls).__new__(cls, name, bases, namespace)
            return self

    class _NoReturn(typing._FinalTypingBase):
        """Special type indicating functions that never return.
        Example::
          from typing import NoReturn
          def stop() -> NoReturn:
              raise Exception('no way')
        This type is invalid in other positions, e.g., ``List[NoReturn]``
        will fail in static type checkers.
        """
        __metaclass__ = NoReturnMeta
        __slots__ = ()

        def __instancecheck__(self, obj):
            raise TypeError("NoReturn cannot be used with isinstance().")

        def __subclasscheck__(self, cls):
            raise TypeError("NoReturn cannot be used with issubclass().")

    NoReturn = _NoReturn(_root=True)


T_co = typing.TypeVar('T_co', covariant=True)

if hasattr(typing, 'ContextManager'):
    ContextManager = typing.ContextManager
else:
    # TODO: Remove once typing.py has been updated
    class ContextManager(typing.Generic[T_co]):
        __slots__ = ()

        def __enter__(self):
            return self

        @abc.abstractmethod
        def __exit__(self, exc_type, exc_value, traceback):
            return None

        @classmethod
        def __subclasshook__(cls, C):
            if cls is ContextManager:
                # In Python 3.6+, it is possible to set a method to None to
                # explicitly indicate that the class does not implement an ABC
                # (https://bugs.python.org/issue25958), but we do not support
                # that pattern here because this fallback class is only used
                # in Python 3.5 and earlier.
                if (any("__enter__" in B.__dict__ for B in C.__mro__) and
                    any("__exit__" in B.__dict__ for B in C.__mro__)):
                    return True
            return NotImplemented


def _collection_protocol(cls):
    # Selected set of collections ABCs that are considered protocols.
    name = cls.__name__
    return (name in ('ABC', 'Callable', 'Awaitable',
                     'Iterable', 'Iterator', 'AsyncIterable', 'AsyncIterator',
                     'Hashable', 'Sized', 'Container', 'Collection', 'Reversible',
                     'Sequence', 'MutableSequence', 'Mapping', 'MutableMapping',
                     'AbstractContextManager', 'ContextManager',
                     'AbstractAsyncContextManager', 'AsyncContextManager',) and
            cls.__module__ in ('collections.abc', 'typing', 'contextlib',
                               '_abcoll', 'abc'))


class _ProtocolMeta(GenericMeta):
    """Internal metaclass for Protocol.

    This exists so Protocol classes can be generic without deriving
    from Generic.
    """

    def __new__(cls, name, bases, namespace,
                tvars=None, args=None, origin=None, extra=None, orig_bases=None):
        # This is just a version copied from GenericMeta.__new__ that
        # includes "Protocol" special treatment. (Comments removed for brevity.)
        assert extra is None  # Protocols should not have extra
        if tvars is not None:
            assert origin is not None
            assert all(isinstance(t, TypeVar) for t in tvars), tvars
        else:
            tvars = _type_vars(bases)
            gvars = None
            for base in bases:
                if base is Generic:
                    raise TypeError("Cannot inherit from plain Generic")
                if (isinstance(base, GenericMeta) and
                        base.__origin__ in (Generic, Protocol)):
                    if gvars is not None:
                        raise TypeError(
                            "Cannot inherit from Generic[...] or"
                            " Protocol[...] multiple times.")
                    gvars = base.__parameters__
            if gvars is None:
                gvars = tvars
            else:
                tvarset = set(tvars)
                gvarset = set(gvars)
                if not tvarset <= gvarset:
                    raise TypeError(
                        "Some type variables (%s) "
                        "are not listed in %s[%s]" %
                        (", ".join(str(t) for t in tvars if t not in gvarset),
                         "Generic" if any(b.__origin__ is Generic
                                          for b in bases) else "Protocol",
                         ", ".join(str(g) for g in gvars)))
                tvars = gvars

        initial_bases = bases
        if extra is None:
            extra = namespace.get('__extra__')
        if extra is not None and type(extra) is abc.ABCMeta and extra not in bases:
            bases = (extra,) + bases
        bases = tuple(b._gorg if isinstance(b, GenericMeta) else b for b in bases)

        if any(isinstance(b, GenericMeta) and b is not Generic for b in bases):
            bases = tuple(b for b in bases if b is not Generic)
        namespace.update({'__origin__': origin, '__extra__': extra})
        self = abc.ABCMeta.__new__(cls, name, bases, namespace)
        abc.ABCMeta.__setattr__(self, '_gorg', self if not origin else origin._gorg)

        self.__parameters__ = tvars
        self.__args__ = tuple(Ellipsis if a is _TypingEllipsis else
                              () if a is _TypingEmpty else
                              a for a in args) if args else None
        self.__next_in_mro__ = _next_in_mro(self)
        if orig_bases is None:
            self.__orig_bases__ = initial_bases
        self.__tree_hash__ = (hash(self._subs_tree()) if origin else
                              abc.ABCMeta.__hash__(self))
        return self

    def __init__(cls, *args, **kwargs):
        super(_ProtocolMeta, cls).__init__(*args, **kwargs)
        if not cls.__dict__.get('_is_protocol', None):
            cls._is_protocol = any(b is Protocol or
                                   isinstance(b, _ProtocolMeta) and
                                   b.__origin__ is Protocol
                                   for b in cls.__bases__)
        if cls._is_protocol:
            for base in cls.__mro__[1:]:
                if not (base in (object, Generic, Callable) or
                        isinstance(base, TypingMeta) and base._is_protocol or
                        isinstance(base, GenericMeta) and base.__origin__ is Generic or
                        _collection_protocol(base)):
                    raise TypeError('Protocols can only inherit from other protocols,'
                                    ' got %r' % base)

            def _no_init(self, *args, **kwargs):
                if type(self)._is_protocol:
                    raise TypeError('Protocols cannot be instantiated')
            cls.__init__ = _no_init

        def _proto_hook(cls, other):
            if not cls.__dict__.get('_is_protocol', None):
                return NotImplemented
            if not isinstance(other, type):
                # Same error as for issubclass(1, int)
                raise TypeError('issubclass() arg 1 must be a new-style class')
            for attr in cls._get_protocol_attrs():
                for base in other.__mro__:
                    if attr in base.__dict__:
                        if base.__dict__[attr] is None:
                            return NotImplemented
                        break
                else:
                    return NotImplemented
            return True
        if '__subclasshook__' not in cls.__dict__:
            cls.__subclasshook__ = classmethod(_proto_hook)

    def __instancecheck__(self, instance):
        # We need this method for situations where attributes are assigned in __init__
        if isinstance(instance, type):
            # This looks like a fundamental limitation of Python 2.
            # It cannot support runtime protocol metaclasses
            return False
        if issubclass(instance.__class__, self):
            return True
        if self._is_protocol:
            return all(hasattr(instance, attr) and getattr(instance, attr) is not None
                       for attr in self._get_protocol_attrs())
        return False

    def __subclasscheck__(self, cls):
        if (self.__dict__.get('_is_protocol', None) and
                not self.__dict__.get('_is_runtime_protocol', None)):
            if sys._getframe(1).f_globals['__name__'] in ['abc', 'functools']:
                return False
            raise TypeError("Instance and class checks can only be used with"
                            " @runtime protocols")
        return super(_ProtocolMeta, self).__subclasscheck__(cls)

    def _get_protocol_attrs(self):
        attrs = set()
        for base in self.__mro__[:-1]:  # without object
            if base.__name__ in ('Protocol', 'Generic'):
                continue
            annotations = getattr(base, '__annotations__', {})
            for attr in list(base.__dict__.keys()) + list(annotations.keys()):
                if (not attr.startswith('_abc_') and attr not in (
                        '__abstractmethods__', '__annotations__', '__weakref__',
                        '_is_protocol', '_is_runtime_protocol', '__dict__',
                        '__args__', '__slots__', '_get_protocol_attrs',
                        '__next_in_mro__', '__parameters__', '__origin__',
                        '__orig_bases__', '__extra__', '__tree_hash__',
                        '__doc__', '__subclasshook__', '__init__', '__new__',
                        '__module__', '_MutableMapping__marker',
                        '__metaclass__', '_gorg') and
                        getattr(base, attr, object()) is not None):
                    attrs.add(attr)
        return attrs

    @_tp_cache
    def __getitem__(self, params):
        # We also need to copy this from GenericMeta.__getitem__ to get
        # special treatment of "Protocol". (Comments removed for brevity.)
        if not isinstance(params, tuple):
            params = (params,)
        if not params and self._gorg is not Tuple:
            raise TypeError(
                "Parameter list to %s[...] cannot be empty" % self.__qualname__)
        msg = "Parameters to generic types must be types."
        params = tuple(_type_check(p, msg) for p in params)
        if self in (Generic, Protocol):
            if not all(isinstance(p, TypeVar) for p in params):
                raise TypeError(
                    "Parameters to %r[...] must all be type variables", self)
            if len(set(params)) != len(params):
                raise TypeError(
                    "Parameters to %r[...] must all be unique", self)
            tvars = params
            args = params
        elif self in (Tuple, Callable):
            tvars = _type_vars(params)
            args = params
        elif self.__origin__ in (Generic, Protocol):
            raise TypeError("Cannot subscript already-subscripted %s" %
                            repr(self))
        else:
            _check_generic(self, params)
            tvars = _type_vars(params)
            args = params

        prepend = (self,) if self.__origin__ is None else ()
        return self.__class__(self.__name__,
                              prepend + self.__bases__,
                              dict(self.__dict__),
                              tvars=tvars,
                              args=args,
                              origin=self,
                              extra=self.__extra__,
                              orig_bases=self.__orig_bases__)


class Protocol(object):
    """Base class for protocol classes. Protocol classes are defined as::

      class Proto(Protocol[T]):
          def meth(self):
              # type: () -> int
              ...

    Such classes are primarily used with static type checkers that recognize
    structural subtyping (static duck-typing), for example::

      class C:
          def meth(self):
              # type: () -> int
              return 0

      def func(x):
          # type: (Proto[int]) -> int
          return x.meth()

      func(C())  # Passes static type check

    See PEP 544 for details. Protocol classes decorated with @typing_extensions.runtime
    act as simple-minded runtime protocols that checks only the presence of
    given attributes, ignoring their type signatures.
    """

    __metaclass__ = _ProtocolMeta
    __slots__ = ()
    _is_protocol = True

    def __new__(cls, *args, **kwds):
        if cls._gorg is Protocol:
            raise TypeError("Type Protocol cannot be instantiated; "
                            "it can be used only as a base class")
        return _generic_new(cls.__next_in_mro__, cls, *args, **kwds)


def runtime(cls):
    """Mark a protocol class as a runtime protocol, so that it
    can be used with isinstance() and issubclass(). Raise TypeError
    if applied to a non-protocol class.

    This allows a simple-minded structural check very similar to the
    one-offs in collections.abc such as Hashable.
    """
    if not isinstance(cls, _ProtocolMeta) or not cls._is_protocol:
        raise TypeError('@runtime can be only applied to protocol classes,'
                        ' got %r' % cls)
    cls._is_runtime_protocol = True
    return cls
