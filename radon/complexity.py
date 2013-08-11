import ast
import math
from radon.visitors import GET_COMPLEXITY, ComplexityVisitor


# sorted_block ordering functions
SCORE = lambda block: -GET_COMPLEXITY(block)
LINES = lambda block: block.lineno
ALPHA = lambda block: block.name


def cc_rank(cc):
    '''Rank the complexity score from A to F, where A stands for the simplest
    and best score and F the most complex and worst one:

    ============= =====================================================
        1 - 5        A (low risk - simple block)
        6 - 10       B (low risk - well structured and stable block)
        11 - 20      C (moderate risk - slightly complex block)
        21 - 30      D (more than moderate risk - more complex block)
        31 - 40      E (high risk - complex block, alarming)
        41+          F (very high risk - error-prone, unstable block)
    ============= =====================================================

    Here *block* is used in place of function, method or class.

    The formula used to convert the score into an index is the following:

    .. math::

        \\text{rank} = \left \lceil \dfrac{\\text{score}}{10} \\right \\rceil
        - H(5 - \\text{score})

    where ``H(s)`` stands for the Heaviside Step Function.
    The rank is then associated to a letter (0 = A, 5 = F).
    '''
    return chr(min(int(math.ceil(cc / 10.) or 1) - (1, 0)[5 - cc < 0], 5) + 65)


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


def sorted_results(blocks, order=SCORE):
    '''Given a ComplexityVisitor instance, returns a list of sorted blocks
    with respect to complexity. A block is a either
    :class:`~radon.visitors.Function` object or a
    :class:`~radon.visitors.Class` object.
    The blocks are sorted in descending order from the block with the highest
    complexity.

    The optional `order` parameter indicates how to sort the blocks. It can be:

        * `LINES`: sort by line numbering;
        * `ALPHA`: sort by name (from A to Z);
        * `SCORE`: sorty by score (descending).

    Default is `SCORE`.
    '''
    return sorted(blocks, key=order)


def cc_visit(code):
    '''Visit the given code with :class:`~radon.visitors.ComplexityVisitor` and
    then pass the result to the :func:`~radon.complexity.sorted_results`
    function.
    '''
    return cc_visit_ast(ast.parse(code))


def cc_visit_ast(ast_node):
    '''Visit the AST node with :class:`~radon.visitors.ComplexityVisitor` and
    pass the resulting blocks to :func:`~radon.complexity.sorted_results`.
    '''
    return sorted_results(ComplexityVisitor.from_ast(ast_node).blocks)
