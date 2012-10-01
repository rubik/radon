import operator
from paramunittest import *
from radon.complexity import *
from radon.visitors import Class, Function


get_index = lambda seq: lambda index: seq[index]


def _compute_rank(score):
    # This is really ugly
    # Luckily the rank function in radon.complexity is not like this!
    if 1 <= score <= 5:
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


RANK_CASES = [(score, _compute_rank(score)) for score in range(1, 100)]


@parametrized(*RANK_CASES)
class TestRank(ParametrizedTestCase):

    def setParameters(self, score, expected_rank):
        self.score = score
        self.expected_rank = expected_rank

    def testRank(self):
        self.assertEqual(rank(self.score), self.expected_rank)


fun = lambda complexity: Function('randomname', 1, 4, False, None, complexity)
cls = lambda complexity: Class('randomname_', 3, 21, [], complexity)

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

    def testSortedResults(self):
        self.assertEqual(sorted_results(self.blocks), self.expected_result)


@parametrized(*SIMPLE_BLOCKS)
class TestAverageComplexity(ParametrizedTestCase):

    def setParameters(self, blocks, _, expected_average):
        self.blocks = blocks
        self.expected_average = expected_average

    def testAverageComplexity(self):
        self.assertEqual(average_complexity(self.blocks),
                         self.expected_average)
