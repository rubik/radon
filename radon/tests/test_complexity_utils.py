import ast
import operator
import unittest
from paramunittest import *
from radon.complexity import *
from radon.visitors import Class, Function
from .test_complexity_visitor import GENERAL_CASES, dedent


get_index = lambda seq: lambda index: seq[index]


def _compute_cc_rank(score):
    # This is really ugly
    # Luckily the rank function in radon.complexity is not like this!
    if score < 0:
        rank = ValueError
    elif 0 <= score <= 5:
        rank = 'A'
    elif 6 <= score <= 10:
        rank = 'B'
    elif 11 <= score <= 20:
        rank = 'C'
    elif 21 <= score <= 30:
        rank = 'D'
    elif 31 <= score <= 40:
        rank = 'E'
    else:
        rank = 'F'
    return rank


RANK_CASES = [(score, _compute_cc_rank(score)) for score in range(-1, 100)]


@parametrized(*RANK_CASES)
class TestRank(ParametrizedTestCase):

    def setParameters(self, score, expected_rank):
        self.score = score
        self.expected_rank = expected_rank

    def test_rank(self):
        if (hasattr(self.expected_rank, '__call__') and
            isinstance(self.expected_rank(), Exception)):
            self.assertRaises(self.expected_rank, cc_rank, self.score)
        else:
            self.assertEqual(cc_rank(self.score), self.expected_rank)


fun = lambda complexity: Function('randomname', 1, 4, 23, False, None, [], complexity)
cls = lambda complexity: Class('randomname_', 3, 21, 18, [], [], complexity)

# This works with both the next two tests
SIMPLE_BLOCKS = [
    ([], [], 0.),
    ([fun(12), fun(14), fun(1)], [1, 0, 2], 9.),
    ([fun(4), cls(5), fun(2), cls(21)], [3, 1, 0, 2], 8.),
]


@parametrized(*SIMPLE_BLOCKS)
class TestSortedResults(ParametrizedTestCase):

    def setParameters(self, blocks, indices, _):
        self.blocks = blocks
        self.expected_result = list(map(get_index(blocks), indices))

    def test_sorted_results(self):
        self.assertEqual(sorted_results(self.blocks), self.expected_result)


@parametrized(*SIMPLE_BLOCKS)
class TestAverageComplexity(ParametrizedTestCase):

    def setParameters(self, blocks, _, expected_average):
        self.blocks = blocks
        self.expected_average = expected_average

    def test_average_complexity(self):
        self.assertEqual(average_complexity(self.blocks),
                         self.expected_average)


CC_VISIT_CASES = [
    (GENERAL_CASES[0][0], 1),
    (GENERAL_CASES[1][0], 3),
    ('''
    class joe1:
        i = 1
        def doit1(self):
            pass
        class joe2:
            ii = 2
            def doit2(self):
                pass
            class joe3:
                iii = 3
                def doit3(self):
                    pass
     ''', 2, 4, 'joe1.joe2.joe3'),
]


@parametrized(*CC_VISIT_CASES)
class TestCCVisit(ParametrizedTestCase):

    def setParameters(self, code, blocks, diff=1, lookfor='f.inner'):
        self.code = dedent(code)
        self.number_of_blocks = blocks
        self.diff = diff
        self.lookfor = lookfor

    def test_cc_visit(self):
        results = cc_visit(self.code)
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), self.number_of_blocks)

    def test_add_inner_blocks(self):
        blocks = cc_visit(self.code)
        with_inner_blocks = add_inner_blocks(blocks)
        names = set(map(operator.attrgetter('name'), with_inner_blocks))
        self.assertEqual(len(with_inner_blocks) - len(blocks), self.diff)
        self.assertTrue(self.lookfor in names)


class TestFlake8Checker(unittest.TestCase):

    def test_run(self):
        c = Flake8Checker(ast.parse(dedent(GENERAL_CASES[0][0])), 'test case')
        self.assertEqual(c.max_cc, -1)
        self.assertEqual(c.no_assert, False)
        self.assertEqual(list(c.run()), [])
        c.max_cc = 3
        self.assertEqual(list(c.run()), [(7, 0, "R701: 'f' is too complex (4)",
                                          type(c))])
