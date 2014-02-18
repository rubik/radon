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

    def testFind(self):
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

    def testLogical(self):
        self.assertEqual(_logical(self.code), self.expected_number_of_lines)


ANALYZE_CASES = [
    ('''
     ''', (0, 0, 0, 0, 0, 0)),

    ('''
     """
     doc?
     """
     ''', (3, 1, 3, 0, 3, 0)),

    ('''
     # just a comment
     if a and b:
         print('woah')
     else:
         # you'll never get here
         print('ven')
     ''', (6, 4, 6, 2, 0, 0)),

    ('''
     #
     #
     #
     ''', (3, 0, 3, 3, 0, 0)),

    ('''
     if a:
         print


     else:
         print
     ''', (6, 4, 4, 0, 0, 2)),

    # In this case the docstring is not counted as a multi-line string
    # because in fact it is on one line!
    ('''
     def f(n):
         """here"""
         return n * f(n - 1)
     ''', (3, 3, 3, 0, 0, 0)),

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
     ''', (12, 9, 11, 2, 4, 1)),

    ('''
     a = [1, 2, 3,
     ''', SyntaxError),
]


@parametrized(*ANALYZE_CASES)
class TestAnalyze(ParametrizedTestCase):

    def setParameters(self, code, expected):
        self.code = dedent(code)
        self.expected = expected

    def testAnalyze(self):
        try:
            len(self.expected)
        except:
            self.assertRaises(self.expected, analyze, self.code)
        else:
            result = analyze(self.code)
            self.assertEqual(result, self.expected)
            # blank + sloc = loc
            self.assertTrue(result[0] == result[2] + result[5])


if __name__ == '__main__':
    import unittest
    unittest.main()
