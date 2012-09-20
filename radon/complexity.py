import math
from radon.visitors import GET_COMPLEXITY, ComplexityVisitor
from radon.utils import iter_filenames, is_dir


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


def visit(code):
    '''Visit the given code with `~radon.visitors.ComplexityVisitor` and
    then pass the result to the `~radon.complexity.sorted_results` function.
    '''
    return sorted_results(ComplexityVisitor.from_code(code))


def visit_package(path):
    '''Visit a whole package. For every module, this function calls
    `~radon.complexity.visit` and yields the result. If the given path points
    to a file, then only that one is visited.
    '''
    def _visit(path):
        with open(path) as fobj:
            return visit(fobj.read())

    if not is_dir(path):
        yield path, _visit(path)
        return
    for module in iter_filenames([path]):
        yield module, _visit(module)
