import ast
import math
from radon.visitors import GET_COMPLEXITY, ComplexityVisitor


def cc_rank(cc):
    '''Rank the complexity score from A to F, where A stands for the simplest
    and best score and F the most complex and worst one::

        1 - 5        A (low risk - simple block)
        6 - 10       B (low risk - well structured and stable block)
        11 - 20      C (moderate risk - slightly complex block)
        21 - 30      D (more than moderate risk - more complex block)
        31 - 40      E (high risk - complex block, alarming)
        41+          F (very high risk - error-prone, unstable block)

    Here *block* is used in place of function, method and class.

    The formula used to convert the score into an index is the following::

        rank = ceil(score / 10) - H(5 - score)

    where H(s) stands for the Heaviside Step Function.
    The rank is then associated to a letter (0 = A, 5 = F).
    '''
    # Lame trick to avoid an if/else block
    # Actually it *is* an if/else block
    return chr(min(int(math.ceil(cc / 10.)) - (1, 0)[5 - cc < 0], 5) + 65)


def average_complexity(blocks):
    '''Compute the average Cyclomatic complexity from the given blocks.
    Blocks must be either :class:`~radon.visitors.Function` or
    :class:`~radon.visitors.Class`. If the block list is empty, then 0 is
    returned.
    '''
    size = len(blocks)
    if size == 0:
        return 0
    return sum((GET_COMPLEXITY(block) for block in blocks), .0) / len(blocks)


def sorted_results(blocks):
    '''Given a ComplexityVisitor instance, returns a list of sorted blocks
    with respect to complexity. A block is a either `~radon.visitors.Function`
    object or a `~radon.visitors.Class` object.
    The blocks are sorted in descending order from the block with the highest
    complexity.
    '''
    return sorted(blocks, key=GET_COMPLEXITY, reverse=True)


def cc_visit(code):
    '''Visit the given code with `~radon.visitors.ComplexityVisitor` and
    then pass the result to the `~radon.complexity.sorted_results` function.
    '''
    return cc_visit_ast(ast.parse(code))


def cc_visit_ast(ast_node):
    '''Visit the AST node with :class:`~radon.visitors.ComplexityVisitor` and
    pass the resulting blocks to :func:`~radon.complexity.sorted_results`.
    '''
    return sorted_results(ComplexityVisitor.from_ast(ast_node).blocks)
