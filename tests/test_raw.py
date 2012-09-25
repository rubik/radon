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
            self.assertRaises(ValueError, _find, self.code, COLON_TYPE, ':')
        else:
            self.assertEqual(_find(self.code, COLON_TYPE, ':'), self.result)


LOGICAL_LINES_CASES = [
    ('''
     # most useless comment
     ''', 1),

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
]


@parametrized(*LOGICAL_LINES_CASES)
class TestLogicalLines(ParametrizedTestCase):

    def setParameters(self, code, expected_number_of_lines):
        self.code = _generate(dedent(code))
        self.expected_number_of_lines = expected_number_of_lines

    def testLogical(self):
        self.assertEqual(_logical(self.code), self.expected_number_of_lines)


if __name__ == '__main__':
    import unittest
    unittest.main()
