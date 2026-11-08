import textwrap
import tokenize

import pytest

from radon.raw import *

dedent = lambda code: textwrap.dedent(code).strip()


FIND_CASES = [
    (
        '''
     return 0
     ''',
        None,
    ),
    (
        '''
     # most useless comment :
     ''',
        None,
    ),
    (
        '''
     if a: pass
     ''',
        2,
    ),
    (
        '''
     # useless comment
     if a: pass
     ''',
        4,
    ),
    (
        '''
     d[3:]
     ''',
        3,
    ),
]


@pytest.mark.parametrize('code,result', FIND_CASES)
def test_find(code, result):
    code = _generate(dedent(code))
    if result is None:
        with pytest.raises(ValueError):
            _find(code, OP, ':')
    else:
        assert _find(code, OP, ':') == result


LOGICAL_LINES_CASES = [
    (
        '''
     ''',
        0,
    ),
    (
        '''
     # most useless comment
     ''',
        0,
    ),
    (
        '''
     a * b + c
     ''',
        1,
    ),
    (
        '''
     if a:
     ''',
        1,
    ),
    (
        '''
     try:
     ''',
        1,
    ),
    (
        '''
     if a:  # just a comment
     ''',
        1,
    ),
    (
        '''
     try:  # just a comment
     ''',
        1,
    ),
    (
        '''
     if a: pass
     ''',
        2,
    ),
    (
        '''
     if a: continue
     ''',
        2,
    ),
    (
        '''
     if a: break
     ''',
        2,
    ),
    (
        '''
     if a: return
     ''',
        2,
    ),
    (
        '''
     if a: pass  # just a comment
     ''',
        2,
    ),
    (
        '''
     if a: continue  # just a comment
     ''',
        2,
    ),
    (
        '''
     if a: break  # just a comment
     ''',
        2,
    ),
    (
        '''
     if a: return  # just a comment
     ''',
        2,
    ),
    (
        '''
     42 # a comment
     ''',
        1,
    ),
    (
        '''
     """
     multiple
     """
     ''',
        1,
    ),
    (
        '''
     # just a comment
     ''',
        0,
    ),
    (
        '''
     a = 2; b = 43
     ''',
        2,
    ),
    (
        '''
     a = 1; b = 2;
     ''',
        2,
    ),
    (
        '''
     a = 2; b = 43; c = 42; d = 3; print(a)
     ''',
        5,
    ),
]


@pytest.mark.parametrize('code,expected_number_of_lines', LOGICAL_LINES_CASES)
def test_logical(code, expected_number_of_lines):
    code = _generate(dedent(code))
    assert _logical(code) == expected_number_of_lines


ANALYZE_CASES = [
    (
        '''
     ''',
        (0, 0, 0, 0, 0, 0, 0),
    ),
    (
        '''
     """
     doc?
     """
     ''',
        (3, 1, 0, 0, 3, 0, 0),
    ),
    (
        '''
     # just a comment
     if a and b:
         print('woah')
     else:
         # you'll never get here
         print('ven')
     ''',
        (6, 4, 4, 2, 0, 0, 2),
    ),
    (
        '''
     #
     #
     #
     ''',
        (3, 0, 0, 3, 0, 0, 3),
    ),
    (
        '''
     if a:
         print


     else:
         print
     ''',
        (6, 4, 4, 0, 0, 2, 0),
    ),
    # In this case the docstring is not counted as a multi-line string
    # because in fact it is on one line!
    (
        '''
     def f(n):
         """here"""
         return n * f(n - 1)
     ''',
        (3, 3, 2, 0, 0, 0, 1),
    ),
    (
        '''
     def hip(a, k):
         if k == 1: return a
         # getting high...
         return a ** hip(a, k - 1)

     def fib(n):
         """Compute the n-th Fibonacci number.

         Try it with n = 294942: it will take a fairly long time.
         """
         if n <= 1: return 1  # otherwise it will melt the cpu
         return fib(n - 2) + fib(n - 1)
     ''',
        (12, 9, 6, 2, 3, 2, 1),
    ),
    (
        '''
     a = [1, 2, 3,
     ''',
        SyntaxError,
    ),
    # Test that handling of parameters with a value passed in.
    (
        '''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
    ''',
        (5, 4, 2, 1, 3, 0, 0),
    ),
    (
        '''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        string = """This is a string not a comment"""
    ''',
        (6, 5, 3, 1, 3, 0, 0),
    ),
    (
        '''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        string = """
                 This is a string not a comment
                 """
    ''',
        (8, 5, 5, 1, 3, 0, 0),
    ),
    (
        '''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        string ="""
                This is a string not a comment
                """
        test = 0
    ''',
        (9, 6, 6, 1, 3, 0, 0),
    ),
    # Breaking lines still treated as single line of code.
    (
        r'''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        string = \
                """
                This is a string not a comment
                """
        test = 0
    ''',
        (10, 6, 7, 1, 3, 0, 0),
    ),
    # Test handling of last line comment.
    (
        r'''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        string =\
                """
                This is a string not a comment
                """
        test = 0
        # Comment
    ''',
        (11, 6, 7, 2, 3, 0, 1),
    ),
    (
        r'''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        test = 0
        string = \
                """
                This is a string not a comment
                """
    ''',
        (10, 6, 7, 1, 3, 0, 0),
    ),
    (
        '''
    def function(
        args
    ):
        """This is a multi-line docstring
        for the function
        """
        pass
    ''',
        (7, 3, 4, 0, 3, 0, 0),
    ),
    (
        '''
    def function():
        multiline_with_equals_in_it = """ """
        pass
    ''',
        (3, 3, 3, 0, 0, 0, 0),
    ),
    (
        '''
    def function():
        """ a docstring in a single line counts as a single-line comment """
    ''',
        (2, 2, 1, 0, 0, 0, 1),
    ),
    (
        '''
    def function():
        """ this is not a """ """ docstring because it is concatenated """
    ''',
        (2, 2, 2, 0, 0, 0, 0),
    ),
    (
        r'''
    def function():
        " this is not a multiline " \
            " docstring "
    ''',
        (3, 2, 3, 0, 0, 0, 0),
    ),
    (
        '''
    def function():
        """ this is not a docstring """ # because it also has a comment on the line
    ''',
        (2, 2, 2, 1, 0, 0, 0),
    ),
    (
        r'''
    def function():
        " a docstring is a not single-line comment when " \
            # followed by a comment on a another line
    ''',
        (3, 2, 3, 1, 0, 0, 0),
    ),
    (
        r'''
    def function():
        """ docstring continued by blank line is not a single-line comment """ \

        pass
    ''',
        (4, 2, 3, 0, 0, 1, 0),
    ),
    (
        r'''
    def function():
        pass; pass
    ''',
        (2, 3, 2, 0, 0, 0, 0),
    ),
    (
        r'''
    def function():
        """ doc string """; pass
    ''',
        (2, 3, 2, 0, 0, 0, 0),
    ),
]


@pytest.mark.parametrize('code,expected', ANALYZE_CASES)
def test_analyze(code, expected):
    code = dedent(code)

    try:
        len(expected)
    except:
        with pytest.raises(expected):
            analyze(code)
    else:
        result = analyze(code)
        assert result == Module(*expected)
        assert (
            result.loc
            == result.blank
            + result.sloc
            + result.single_comments
            + result.multi
        )


@pytest.mark.parametrize('opening,line,closing', [
    ('values = [', '1,', ']'),
    ('values = {', '"key": 1,', '}'),
    ('"""', 'docstring text', '"""'),
])
def test_analyze_multiline_tokenization_is_linear(monkeypatch,
                                                opening, line, closing):
    source = '\n'.join([opening] + [line] * 128 + [closing])
    generate_tokens = tokenize.generate_tokens
    consumed = []

    def counted_tokens(readline):
        def counted_readline():
            text = readline()
            consumed.append(len(text))
            return text
        return generate_tokens(counted_readline)

    monkeypatch.setattr(tokenize, 'generate_tokens', counted_tokens)
    result = analyze(source)

    assert result.loc == 130
    assert result.lloc == (2 if opening == 'values = {' else 1)
    assert result.multi == (130 if opening == '"""' else 0)
    # Count input consumed by the tokenizer rather than elapsed wall time.
    assert sum(consumed) <= 2 * len(source)


def test_analyze_multiline_groups_keep_following_lines_separate():
    source = '\n'.join([
        'values = [', '1,  # first', '', '2,', ']',
        '# following comment', '"""following docstring"""', 'result = 3',
    ])

    assert analyze(source) == Module(8, 3, 5, 2, 0, 1, 2)


@pytest.mark.parametrize('ending', ['[1,', '"""text', '"text', '\\'])
def test_analyze_unfinished_group_reports_starting_line(ending):
    with pytest.raises(SyntaxError, match='SyntaxError at line: 2'):
        analyze('# first line\nvalue = ' + ending)
