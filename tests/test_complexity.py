import textwrap
from paramunittest import *
from radon.visitors import ComplexityVisitor


BLOCKS_CASES = [
    ('''
    if a and b: pass
    ''', 3),

    ('''
    if a and b: pass
    else: pass
    ''', 4),

    ('''
     if a and b: pass
     elif c and d: pass
     else: pass
     ''', 6),

    ('''
     if (a and b) or (c and d): pass
     else: pass
     ''', 6),

    ('''
     if a and b or c: pass
     else: pass
     ''', 5),

    ('''
     for x in range(10): print x
     ''', 2),

    ('''
     for x in xrange(10): print x
     else: pass
     ''', 3),

    ('''
     while a < 4: pass
     ''', 2),

    ('''
     while a < 4: pass
     else: pass
     ''', 3),

    ('''
     while a < 4 and b < 42: pass
     ''', 3),

    ('''
     while a and b or c < 10: pass
     else: pass
     ''', 5),

    ('''
     with open('raw.py') as fobj: print fobj.read()
     ''', 2),

    ('''
     [i for i in range(4)]
     ''', 2),

    ('''
     [i for i in range(4) if i&1]
     ''', 3),

    ('''
     (i for i in range(4))
     ''', 2),

    ('''
     (i for i in range(4) if i&1)
     ''', 3),

    ('''
     {i for i in range(4)}
     ''', 2),

    ('''
     {i for i in range(4) if i&1}
     ''', 3),

    ('''
     {i:i**4 for i in range(4)}
     ''', 2),

    ('''
     {i:i**4 for i in range(4) if i&1}
     ''', 3),

    ('''
     try: raise TypeError
     except TypeError: pass
     ''', 2),

    ('''
     try: raise TypeError
     except TypeError: pass
     else: pass
     ''', 3),

    ('''
     try: raise TypeError
     finally: pass
     ''', 2),

    ('''
     try: raise TypeError
     except TypeError: pass
     finally: pass
     ''', 3),

    ('''
     try: raise TypeError
     except TypeError: pass
     else: pass
     finally: pass
     ''', 4),

    ('''
     k = lambda a, b: k(b, a)
     ''', 2),
]


FUNCTIONS_CASES = [
    ('''
     def f(a, b, c):
        if a and b == 4:
            return c ** c
        elif a and not c:
            return sum(i for i in range(41) if i&1)
        return a + b
     ''', (1, 7)),

    ('''

     if a and not b: pass
     elif b or c: pass
     else: pass

     for i in range(4):
        print i

     def g(a, b):
        while a < b:
            b, a = a **2, b ** 2
        return b
     ''', (7, 2))
]


@parametrized(*BLOCKS_CASES)
class TestSimpleBlocks(ParametrizedTestCase):

    def setParameters(self, code, expected_complexity):
        self.code = textwrap.dedent(code).strip()
        self.expected_complexity = expected_complexity

    def testComplexityVisitor(self):
        visitor = ComplexityVisitor.from_code(self.code)
        self.assertEqual(visitor.complexity, self.expected_complexity)


@parametrized(*FUNCTIONS_CASES)
class TestFunctions(ParametrizedTestCase):

    def setParameters(self, code, expected_complexity):
        self.code = textwrap.dedent(code).strip()
        self.expected_complexity = expected_complexity

    def testComplexityVisitor(self):
        visitor = ComplexityVisitor.from_code(self.code)
        self.assertEqual(len(visitor.functions), 1)
        self.assertEqual((visitor.complexity, visitor.functions[0].complexity),
                         self.expected_complexity)


if __name__ == '__main__':
    import unittest
    unittest.main()
