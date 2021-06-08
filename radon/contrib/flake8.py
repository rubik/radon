from radon.complexity import add_inner_blocks
from radon.visitors import ComplexityVisitor


class Flake8Checker(object):
    '''Entry point for the Flake8 tool.'''

    name = 'radon'
    version = __import__('radon').__version__
    _code = 'R701'
    _error_tmpl = 'R701 %r is too complex (%d)'
    no_assert = False
    show_closures = False
    max_cc = -1

    def __init__(self, tree, filename):
        '''Accept the AST tree and a filename (unused).'''
        self.tree = tree

    @classmethod
    def add_options(cls, option_manager):  # pragma: no cover
        '''Add custom options to the global parser.'''
        option_manager.add_option(
            '--radon-max-cc',
            default=-1,
            action='store',
            type=int,
            help='Radon complexity threshold',
            parse_from_config=True,
        )
        option_manager.add_option(
            '--radon-no-assert',
            dest='no_assert',
            action='store_true',
            default=False,
            help='Radon will ignore assert statements',
            parse_from_config=True,
        )
        option_manager.add_option(
            '--radon-show-closures',
            dest='show_closures',
            action='store_true',
            default=False,
            help='Add closures/inner classes to the output',
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, options):  # pragma: no cover
        '''Save actual options as class attributes.'''
        cls.max_cc = options.radon_max_cc
        cls.no_assert = options.no_assert
        cls.show_closures = options.show_closures

    def run(self):
        '''Run the ComplexityVisitor over the AST tree.'''
        if self.max_cc < 0:
            if not self.no_assert:
                return
            self.max_cc = 10
        visitor = ComplexityVisitor.from_ast(
            self.tree, no_assert=self.no_assert
        )

        blocks = visitor.blocks
        if self.show_closures:
            blocks = add_inner_blocks(blocks)

        for block in blocks:
            if block.complexity > self.max_cc:
                text = self._error_tmpl % (block.name, block.complexity)
                yield block.lineno, block.col_offset, text, type(self)
