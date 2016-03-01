import textwrap
from paramunittest import *
from radon.raw import *


dedent = lambda code: textwrap.dedent(code).strip()


FIND_CASES = [
    ('''
     return 0
     ''', None),

    ('''
     # most useless comment :
     ''', None),

    ('''
     if a: pass
     ''', 2),

    ('''
     # useless comment
     if a: pass
     ''', 4),

    ('''
     d[3:]
     ''', 3),
]


@parametrized(*FIND_CASES)
class TestFind(ParametrizedTestCase):

    def setParameters(self, code, result):
        self.code = _generate(dedent(code))
        self.result = result

    def test_find(self):
        if self.result is None:
            self.assertRaises(ValueError, _find, self.code, OP, ':')
        else:
            self.assertEqual(_find(self.code, OP, ':'), self.result)


LOGICAL_LINES_CASES = [
    ('''
     ''', 0),

    ('''
     # most useless comment
     ''', 0),

    ('''
     a * b + c
     ''', 1),

    ('''
     if a:
     ''', 1),

    ('''
     try:
     ''', 1),

    ('''
     if a:  # just a comment
     ''', 1),

    ('''
     try:  # just a comment
     ''', 1),

    ('''
     if a: pass
     ''', 2),

    ('''
     if a: continue
     ''', 2),

    ('''
     if a: break
     ''', 2),

    ('''
     if a: return
     ''', 2),

    ('''
     if a: pass  # just a comment
     ''', 2),

    ('''
     if a: continue  # just a comment
     ''', 2),

    ('''
     if a: break  # just a comment
     ''', 2),

    ('''
     if a: return  # just a comment
     ''', 2),

    ('''
     42 # a comment
     ''', 1),

    ('''
     """
     multiple
     """
     ''', 1),

    ('''
     # just a comment
     ''', 0),

    ('''
     a = 2; b = 43
     ''', 2),

    ('''
     a = 1; b = 2;
     ''', 2),
]


@parametrized(*LOGICAL_LINES_CASES)
class TestLogicalLines(ParametrizedTestCase):

    def setParameters(self, code, expected_number_of_lines):
        self.code = _generate(dedent(code))
        self.expected_number_of_lines = expected_number_of_lines

    def test_logical(self):
        self.assertEqual(_logical(self.code), self.expected_number_of_lines)


ANALYZE_CASES = [
    ('''
     ''', (0, 0, 0, 0, 0, 0, 0)),

    ('''
     """
     doc?
     """
     ''', (0, 1, 3, 0, 3, 0, 0)),

    ('''
     # just a comment
     if a and b:
         print('woah')
     else:
         # you'll never get here
         print('ven')
     ''', (4, 4, 6, 2, 0, 0, 2)),

    ('''
     #
     #
     #
     ''', (0, 0, 3, 3, 0, 0, 3)),

    ('''
     if a:
         print


     else:
         print
     ''', (4, 4, 4, 0, 0, 2, 0)),

    # In this case the docstring is not counted as a multi-line string
    # because in fact it is on one line!
    ('''
     def f(n):
         """here"""
         return n * f(n - 1)
     ''', (2, 3, 3, 0, 0, 0, 1)),

    ('''
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
     ''', (6, 9, 10, 2, 3, 1, 1)),

    ('''
     a = [1, 2, 3,
     ''', SyntaxError),

    # Test that handling of parameters with a value passed in.
    ('''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
    ''', (2, 4, 5, 1, 3, 0, 0)),

    ('''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        string = """This is a string not a comment"""
    ''', (3, 5, 6, 1, 3, 0, 0)),

    ('''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        string = """
                 This is a string not a comment
                 """
    ''', (5, 5, 8, 1, 3, 0, 0)),

    ('''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        string ="""
                This is a string not a comment
                """
        test = 0
    ''', (6, 6, 9, 1, 3, 0, 0)),

    # Breaking lines still treated as single line of code.
    ('''
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
    ''', (6, 6, 9, 1, 3, 0, 0)),

    # Test handling of last line comment.
    ('''
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
    ''', (6, 6, 10, 2, 3, 0, 1)),

    ('''
     def foo(n=1):
        """
        Try it with n = 294942: it will take a fairly long time.
        """
        if n <= 1: return 1  # otherwise it will melt the cpu
        test = 0
        string =\
                """
                This is a string not a comment
                """
    ''', (6, 6, 9, 1, 3, 0, 0)),

    ('''
    def function(
        args
    ):
        """This is a multi-line docstring
        for the function
        """
        pass
    ''', (4, 3, 7, 0, 3, 0, 0)),
]


@parametrized(*ANALYZE_CASES)
class TestAnalyze(ParametrizedTestCase):

    def setParameters(self, code, expected):
        self.code = dedent(code)
        self.expected = expected

    def test_analyze(self):
        try:
            len(self.expected)
        except:
            self.assertRaises(self.expected, analyze, self.code)
        else:
            result = analyze(self.code)
            self.assertEqual(result, self.expected)
            # sloc - single_comments - multi  = loc
            self.assertTrue(result[0] == result[2] - result[6] - result[4])
