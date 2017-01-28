from typing_inspect import is_generic_type
from unittest import TestCase, main


class IsUtilityTestCase(TestCase):
    def sample_test(self, fun, samples, nonsamples):
        for s in samples:
            self.assertTrue(fun(s))
        for s in nonsamples:
            self.assertFalse(fun(s))

    def test_generic(self):
        samples = []
        nonsamples = []
        self.sample_test(is_generic_type, samples, nonsamples)


if __name__ == '__main__':
    main()
