import textwrap
from paramunittest import *
from radon.metrics import *


dedent = lambda code: textwrap.dedent(code).strip()


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


H_VISIT_CASES = [
    ('''
     ''', (0,) * 12),

    ('''
     a = b + c
     d = c - f

     def f(b):
         a = 2 - 4
         d = a + b
         return a ** d
     ''', (3, 8, 5, 10, 11, 15, 28.75488750216347, 51.89147427955947,
           1.875, 97.296514274174, 5.405361904120777, 0.01729715809318649)),
]


@parametrized(*H_VISIT_CASES)
class TestHVisit(ParametrizedTestCase):

    def setParameters(self, code, expected):
        self.code = dedent(code)
        self.expected = expected

    def testHVisit(self):
        self.assertEqual(h_visit(self.code), self.expected)


if __name__ == '__main__':
    import unittest
    unittest.main()
