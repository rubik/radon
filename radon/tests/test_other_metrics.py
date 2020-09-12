import textwrap

import pytest

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
    ((0, 0, 0, 0), 100.0),
    ((0, 1, 2, 0), 100.0),
    ((10, 2, 5, 0.5), 81.75051711476864),
    ((200, 10, 78, 45), 70.0321877686122),
]


@pytest.mark.parametrize('values,expected', MI_COMPUTE_CASES)
def test_mi_compute(values, expected):
    # Equivalent to unittest's assertAlmostEqual
    assert round(mi_compute(*values) - expected, 5) == 0


MI_RANK_CASES = [(score, _compute_mi_rank(score)) for score in range(0, 100)]


@pytest.mark.parametrize('score,expected', MI_RANK_CASES)
def test_mi_rank(score, expected):
    assert mi_rank(score) == expected


H_VISIT_CASES = [
    (
        '''
     ''',
        ((0,) * 12, []),
    ),
    (
        '''
     a = b + c
     d = c - f

     def f(b):
         a = 2 - 4
         d = a + b
         return a ** d
     ''',
        (
            (
                3,
                8,
                5,
                10,
                11,
                15,
                28.75488750216347,
                51.89147427955947,
                1.875,
                97.296514274174,
                5.405361904120777,
                0.01729715809318649,
            ),
            [
                (
                    "f",
                    (
                        3,
                        5,
                        3,
                        6,
                        8,
                        9,
                        16.36452797660028028366,
                        26.99999999999999999987,
                        1.8,
                        48.59999999999999999977,
                        2.69999999999999999999,
                        0.00900000000000000000,
                    ),
                )
            ],
        ),
    ),
]


@pytest.mark.parametrize('code,expected', H_VISIT_CASES)
def test_h_visit(code, expected):
    code = dedent(code)
    # test for almost-equality
    for act, exp in zip(h_visit(code), expected):
        for a, e in zip(act, exp):
            assert a == e or int(a * 10 ** 3) == int(e * 10 ** 3)


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
    (
        '''
     ''',
        100.0,
        True,
    ),
    (
        '''
     ''',
        100.0,
        False,
    ),
    # V = 41.51317942364757
    # CC = 1
    # LLOC = 4
    # CM % = 0
    (first_mi, 75.40162245189028, True),
    (first_mi, 75.40162245189028, False),
    # V = 66.60791492653966
    # CC = 4
    # LLOC = 9
    # CM % = 38.46153846153847
    (second_mi, 93.84027450359395, True),
    # CM % = 15.384615384615385
    (second_mi, 88.84176333569131, False),
]


@pytest.mark.parametrize('code,expected,count_multi', MI_VISIT_CASES)
def test_mi_visit(code, expected, count_multi):
    code = dedent(code)
    expected = expected
    count_multi = count_multi
    assert mi_visit(code, count_multi) == expected
