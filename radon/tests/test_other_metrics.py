from paramunittest import *
from radon.metrics import *


COMPUTE_MI_CASES = [
    ((0, 0, 0, 0), 100.),
    ((0, 1, 2, 0), 100.),
    ((10, 2, 5, .5), 81.75051711476864),
    ((200, 10, 78, 45), 70.0321877686122),
]


@parametrized(*COMPUTE_MI_CASES)
class TestComputeMI(ParametrizedTestCase):

    def setParameters(self, values, expected):
        self.values = values
        self.expected = expected

    def testComputeMI(self):
        self.assertAlmostEqual(compute_mi(*self.values), self.expected)


if __name__ == '__main__':
    import unittest
    unittest.main()
