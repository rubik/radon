'''Tests for the suppression module.'''

import pytest

from radon.suppression import (
    get_ignore_lines,
    should_ignore_block,
    filter_ignored_blocks,
)
from radon.complexity import cc_visit, add_inner_blocks
from radon.visitors import Function, Class


# Sample code snippets for testing
CODE_WITH_IGNORE_ON_FUNCTION = '''
def normal_function(x):
    if x > 0:
        return x
    return -x

def ignored_function(x):  # radon: ignore
    if x > 0:
        if x > 10:
            return x * 2
    return x
'''

CODE_WITH_IGNORE_BEFORE_FUNCTION = '''
# radon: ignore
def ignored_function(x):
    if x > 0:
        if x > 10:
            return x * 2
    return x

def normal_function(x):
    if x > 0:
        return x
    return -x
'''

CODE_WITH_IGNORE_ON_CLASS = '''
class NormalClass:
    def method(self, x):
        if x > 0:
            return x
        return -x

class IgnoredClass:  # radon: ignore
    def method(self, x):
        if x > 0:
            return x
        return -x
'''

CODE_WITH_IGNORE_CLOSURE = '''
def outer_function(x):
    def inner_ignored(y):  # radon: ignore
        if y > 10:
            return y * 2
        elif y > 5:
            return y + 1
        return y

    def inner_normal(y):
        if y > 0:
            return y
        return -y

    return inner_normal(x)
'''

CODE_WITH_VARIOUS_FORMATS = '''
def func1():  # radon: ignore
    pass

def func2():  #radon:ignore
    pass

def func3():  # RADON: IGNORE
    pass

def func4():  # radon: ignore extra text
    pass

def func5():
    pass
'''


class TestGetIgnoreLines:
    '''Tests for get_ignore_lines function.'''

    def test_empty_source(self):
        assert get_ignore_lines('') == set()

    def test_no_ignore_comments(self):
        code = '''
def foo():
    return 1
'''
        assert get_ignore_lines(code) == set()

    def test_single_ignore_comment(self):
        code = '''
def foo():  # radon: ignore
    return 1
'''
        lines = get_ignore_lines(code)
        assert 2 in lines

    def test_multiple_ignore_comments(self):
        code = '''
def foo():  # radon: ignore
    return 1

def bar():
    # radon: ignore
    return 2
'''
        lines = get_ignore_lines(code)
        assert 2 in lines
        assert 6 in lines

    def test_case_insensitive(self):
        code = '''
def foo():  # RADON: IGNORE
    return 1

def bar():  # Radon: Ignore
    return 2
'''
        lines = get_ignore_lines(code)
        assert len(lines) == 2

    def test_various_spacing(self):
        code = '''
def foo():  # radon:ignore
    return 1

def bar():  #radon: ignore
    return 2

def baz():  #  radon:  ignore
    return 3
'''
        lines = get_ignore_lines(code)
        assert len(lines) == 3


class TestShouldIgnoreBlock:
    '''Tests for should_ignore_block function.'''

    def test_no_ignore_lines(self):
        block = Function('foo', 1, 0, 5, False, None, [], 3)
        assert should_ignore_block(block, set()) is False

    def test_ignore_on_definition_line(self):
        block = Function('foo', 1, 0, 5, False, None, [], 3)
        assert should_ignore_block(block, {1}) is True

    def test_ignore_line_before_block(self):
        # Ignore comment on line 0 (before block starting on line 1)
        block = Function('foo', 1, 0, 5, False, None, [], 3)
        assert should_ignore_block(block, {0}) is True

    def test_ignore_inside_block_not_ignored(self):
        # Ignore comment inside block (line 3) does NOT ignore the block
        # Only definition line or line before counts
        block = Function('foo', 1, 0, 5, False, None, [], 3)
        assert should_ignore_block(block, {3}) is False

    def test_ignore_outside_block(self):
        block = Function('foo', 1, 0, 5, False, None, [], 3)
        assert should_ignore_block(block, {10}) is False


class TestFilterIgnoredBlocks:
    '''Tests for filter_ignored_blocks function.'''

    def test_no_ignore_lines(self):
        blocks = [
            Function('foo', 1, 0, 5, False, None, [], 3),
            Function('bar', 10, 0, 15, False, None, [], 2),
        ]
        result = filter_ignored_blocks(blocks, set())
        assert len(result) == 2

    def test_filter_one_block(self):
        blocks = [
            Function('foo', 1, 0, 5, False, None, [], 3),
            Function('bar', 10, 0, 15, False, None, [], 2),
        ]
        result = filter_ignored_blocks(blocks, {1})
        assert len(result) == 1
        assert result[0].name == 'bar'

    def test_filter_all_blocks(self):
        blocks = [
            Function('foo', 1, 0, 5, False, None, [], 3),
            Function('bar', 10, 0, 15, False, None, [], 2),
        ]
        # Line 1 is foo's definition, line 10 is bar's definition
        result = filter_ignored_blocks(blocks, {1, 10})
        assert len(result) == 0


class TestCCVisitWithSuppression:
    '''Integration tests for cc_visit with suppression.'''

    def test_ignore_function_on_definition(self):
        blocks = cc_visit(CODE_WITH_IGNORE_ON_FUNCTION)
        names = [b.name for b in blocks]
        assert 'normal_function' in names
        assert 'ignored_function' not in names

    def test_ignore_function_before_definition(self):
        blocks = cc_visit(CODE_WITH_IGNORE_BEFORE_FUNCTION)
        names = [b.name for b in blocks]
        assert 'normal_function' in names
        assert 'ignored_function' not in names

    def test_ignore_class(self):
        blocks = cc_visit(CODE_WITH_IGNORE_ON_CLASS)
        names = [b.name for b in blocks]
        assert 'NormalClass' in names
        assert 'IgnoredClass' not in names

    def test_ignore_suppression_disabled(self):
        '''Test that ignore_suppression=True keeps all blocks.'''
        blocks = cc_visit(CODE_WITH_IGNORE_ON_FUNCTION, ignore_suppression=True)
        names = [b.name for b in blocks]
        assert 'normal_function' in names
        assert 'ignored_function' in names

    def test_various_comment_formats(self):
        blocks = cc_visit(CODE_WITH_VARIOUS_FORMATS)
        names = [b.name for b in blocks]
        # Only func5 should remain (no ignore comment)
        assert names == ['func5']


class TestAddInnerBlocksWithSuppression:
    '''Tests for add_inner_blocks with ignore_lines.'''

    def test_ignore_closure(self):
        blocks = cc_visit(CODE_WITH_IGNORE_CLOSURE, ignore_suppression=True)
        ignore_lines = get_ignore_lines(CODE_WITH_IGNORE_CLOSURE)
        expanded = add_inner_blocks(blocks, ignore_lines=ignore_lines)
        names = [b.name for b in expanded]
        assert 'outer_function' in names
        assert 'outer_function.inner_normal' in names
        assert 'outer_function.inner_ignored' not in names
