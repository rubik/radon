import textwrap
from paramunittest import *
from radon.metrics import *


dedent = lambda code: textwrap.dedent(code).strip()

def _compute_mi_rank(score):
    if 0 <= score < 10:
        res = 'C'
    elif 10 <= score < 20:
        res = 'B'
    elif 20 <= score <= 100:
        res = 'A'
    else:
        raise ValueError(score)
    return res


MI_COMPUTE_CASES = [
    ((0, 0, 0, 0), 100.),
    ((0, 1, 2, 0), 100.),
    ((10, 2, 5, .5), 81.75051711476864),
    ((200, 10, 78, 45), 70.0321877686122),
]


@parametrized(*MI_COMPUTE_CASES)
class TestComputeMI(ParametrizedTestCase):

    def setParameters(self, values, expected):
        self.values = values
        self.expected = expected

    def testComputeMI(self):
        self.assertAlmostEqual(mi_compute(*self.values), self.expected)


MI_RANK_CASES = [(score, _compute_mi_rank(score)) for score in range(0, 100)]


@parametrized(*MI_RANK_CASES)
class TestMIRank(ParametrizedTestCase):

    def setParameters(self, score, expected_rank):
        self.score = score
        self.expected_rank = expected_rank

    def testRank(self):
        self.assertEqual(mi_rank(self.score), self.expected_rank)


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


first_mi = '''
     def f(a, b, c):
         return (a ** b) % c

     k = f(1, 2, 3)
     print(k ** 2 - 1)
'''

second_mi = '''
     class A(object):

         def __init__(self, n):
             # this is awesome
             self.n = sum(i for i in range(n) if i&1)

         def m(self, j):
             """Just compute it.
             Example.
             """
             if j > 421:
                 return (self.n + 2) ** j
             return (self.n - 2) ** j

     a = A(4)
     a.m(42)  # i don't know why, but it works
'''

MI_VISIT_CASES = [
    ('''
     ''', 100., True),

    ('''
     ''', 100., False),

    # V = 41.51317942364757
    # CC = 1
    # LLOC = 4
    # CM % = 0
    (first_mi, 75.40162245189028, True),
    (first_mi, 75.40162245189028, False),

    # V = 66.60791492653966
    # CC = 4
    # LLOC = 10
    # CM % = 38.46153846153847
    (second_mi, 92.93379997479954, True),

    # CM % = 15.384615384615385
    (second_mi, 86.11274278663237, False),
]


@parametrized(*MI_VISIT_CASES)
class TestMIVisit(ParametrizedTestCase):

    def setParameters(self, code, expected, count_multi):
        self.code = dedent(code)
        self.expected = expected
        self.count_multi = count_multi

    def testMIParameters(self):
        self.assertEqual(mi_visit(self.code, self.count_multi), self.expected)
