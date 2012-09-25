import ast
import math
import collections
from radon.visitors import HalsteadVisitor
from radon.complexity import cc_visit_ast, average_complexity
from radon.raw import analyze


# Halstead metrics
Halstead = collections.namedtuple('Halstead', 'h1 h2 N1 N2 vocabulary length '
                                              'calculated_length volume '
                                              'difficulty effort time bugs')


def compute_mi(halstead_volume, complexity, sloc):
    return max(0, (171 - 5.2 * math.log(halstead_volume) - .23 * complexity -
                   16.2 * math.log(sloc)) * 100 / 171.)


def h_visit(code):
    return h_visit_ast(ast.parse(code))


def h_visit_ast(ast_node):
    visitor = HalsteadVisitor.from_ast(ast_node)
    h1, h2 = visitor.distinct_operators, visitor.distinct_operands
    N1, N2 = visitor.operators, visitor.operands
    h = h1 + h2
    N = N1 + N2
    volume = math.log(h ** N, 2)
    difficulty = (h1 * N2) / float(2 * h2)
    effort = difficulty * volume
    return Halstead(
        h1, h2, N1, N2, h, N, math.log(h1 ** h1, 2) + math.log(h2 ** h2, 2),
        volume, difficulty, effort, effort / 18., volume / 3000.
    )


def mi_parameters(code):
    ast_node = ast.parse(code)
    return (h_visit_ast(ast_node).volume,
            average_complexity(cc_visit_ast(ast_node)),
            analyze(code).sloc)


def mi_visit(code):
    return compute_mi(*mi_parameters(code))
