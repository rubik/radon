import ast
import math
from radon.visitors import GET_COMPLEXITY, ComplexityVisitor


def rank(complexity):
    '''Rank the complexity score from A to F, where A stands for the simplest
    and best score and F the most complex and worst one.

    The score is computed with the following formula:

        partial = floor(abs((ceil(complexity) - 1) / 10))
        score = min(partial, 6)

    An intermediate step is necessary since the score could get greater than
    6 and 6 is the maximum allowed.
    The score is then associated to a letter:

        0 -> A
        1 -> B
          ..
        4 -> E
        5 -> F
    '''
    partial = int(abs((math.ceil(complexity) - 1) / 10.))
    return chr(min(partial, 5) + 65)


def average_complexity(blocks):
    return sum((GET_COMPLEXITY(block) for block in blocks), .0) / len(blocks)


def sorted_results(visitor):
    '''Given a ComplexityVisitor instance, returns a list of sorted blocks
    with respect to complexity. A block is a either `~radon.visitors.Function`
    object or a `~radon.visitors.Class` object.
    The blocks are sorted in descending order from the block with the highest
    complexity.
    '''
    blocks = visitor.functions
    for cls in visitor.classes:
        blocks.extend(cls.methods)
        blocks.append(cls)
    blocks.sort(key=GET_COMPLEXITY, reverse=True)
    return blocks


def cc_visit(code):
    '''Visit the given code with `~radon.visitors.ComplexityVisitor` and
    then pass the result to the `~radon.complexity.sorted_results` function.
    '''
    return cc_visit_ast(ast.parse(code))


def cc_visit_ast(ast_node):
    return sorted_results(ComplexityVisitor.from_ast(ast_node))
