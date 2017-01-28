from typing_inspect import is_generic_type
from unittest import TestCase, main
from typing import (
    Union, ClassVar, Callable, Optional, TypeVar, Sequence, Mapping,
    MutableMapping, Iterable, Generic, List
)


class IsUtilityTestCase(TestCase):
    def sample_test(self, fun, samples, nonsamples):
        for s in samples:
            self.assertTrue(fun(s))
        for s in nonsamples:
            self.assertFalse(fun(s))

    def test_generic(self):
        T = TypeVar('T')
        samples = [Generic, Generic[T], Iterable[int], Mapping,
                   MutableMapping[T, List[int]], Sequence[Union[str, bytes]]]
        nonsamples = [int, Union[int, str], Union[int, T], ClassVar[List[int]],
                      Callable[..., T], ClassVar, Optional, bytes, list]
        self.sample_test(is_generic_type, samples, nonsamples)


if __name__ == '__main__':
    main()
