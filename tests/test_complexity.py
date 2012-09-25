import sys
import textwrap
from paramunittest import *
from radon.visitors import ComplexityVisitor, GET_COMPLEXITY


dedent = lambda code: textwrap.dedent(code).strip()


BLOCKS_CASES = [
    ('''
     if a: pass
     ''', 2),

    ('''
     if a: pass
     else: pass
     ''', 2),

    ('''
     if a: pass
     elif b: pass
     ''', 3),

    ('''
     if a: pass
     elif b: pass
     else: pass
     ''', 3),

    ('''
    if a and b: pass
    ''', 3),

    ('''
    if a and b: pass
    else: pass
    ''', 3),

    ('''
     if a and b: pass
     elif c and d: pass
     else: pass
     ''', 5),

    ('''
     if a and b or c and d: pass
     else: pass
     ''', 5),

    ('''
     if a and b or c: pass
     else: pass
     ''', 4),

    ('''
     for x in range(10): print(x)
     ''', 2),

    ('''
     for x in xrange(10): print(x)
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
     with open('raw.py') as fobj: print(fobj.read())
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
     [i for i in range(42) if sum(k ** 2 for k in divisors(i)) & 1]
     ''', 4),

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

    ('''
     v = a if b else c
     ''', 2),

    ('''
     v = a if sum(i for i in xrange(c)) < 10 else c
     ''', 3),
]


# These run only if Python version is >= 2.7
ADDITIONAL_BLOCKS = [
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
]


SINGLE_FUNCTIONS_CASES = [
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
        print(i)

     def g(a, b):
        while a < b:
            b, a = a **2, b ** 2
        return b
     ''', (6, 2)),

    ('''
     def f(a, b):
        while a**b:
            a, b = b, a * (b - 1)
            if a and b:
                b = 0
            else:
                b = 1
        return sum(i for i in range(b))
     ''', (1, 5)),
]


FUNCTIONS_CASES = [
    ('''
     def f(a, b):
        return a if b else 2

     def g(a, b, c):
        if a and b:
            return a / b + b / a
        elif b and c:
            return b / c - c / b
        return a + b + c

     def h(a, b):
        return 2 * (a + b)
     ''', (2, 5, 1)),

    ('''
     def f(p, q):
        while p:
            p, q = q, p - q
        if q < 1:
            return 1 / q ** 2
        elif q > 100:
            return 1 / q ** .5
        return 42 if not q else p

     def g(a, b, c):
        if a and b or a - b:
            return a / b - c
        elif b or c:
            return 1
        else:
            k = 0
            with open('results.txt', 'w') as fobj:
                for i in range(b ** c):
                    k += sum(1 / j for j in range(i ** 2) if j > 2)
                fobj.write(str(k))
            return k - 1
     ''', (5, 10)),
]


CLASSES_CASES = [
    ('''
     class A(object):

         def m(self, a, b):
             if not a or b:
                 return b - 1
             try:
                 return a / b
             except ZeroDivisionError:
                 return a
        
         def n(self, k):
             while self.m(k) < k:
                 k -= self.m(k ** 2 - min(self.m(j) for j in range(k ** 4)))
             return k
     ''', (6, 4, 3)),

    ('''
     class B(object):

         ATTR = 9 if A().n(9) == 9 else 10
         import sys
         if sys.version_info >= (3, 3):
             import os
             AT = os.openat('/random/loc')
         
         def __iter__(self):
             return __import__('itertools').tee(B.__dict__)

         def test(self, func):
             a = func(self.ATTR, self.AT)
             if a < self.ATTR:
                 yield self
             elif a > self.ATTR ** 2:
                 yield self.__iter__()
             yield iter(a)
     ''', (5, 1, 3)),
]


class BlocksMixin(object):

    def setParameters(self, code, expected_complexity):
        self.code = dedent(code)
        self.expected_complexity = expected_complexity

    def testComplexityVisitor(self):
        visitor = ComplexityVisitor.from_code(self.code)
        self.assertEqual(visitor.complexity, self.expected_complexity)


@parametrized(*BLOCKS_CASES)
class TestSimpleBlocks(BlocksMixin, ParametrizedTestCase):
    '''Test simple blocks.'''


if sys.version_info[:2] >= (2, 7):
    @parametrized(*ADDITIONAL_BLOCKS)
    class TestAdditionalBlocks(BlocksMixin, ParametrizedTestCase):
        '''Test set and dict comprehensions.'''


@parametrized(*SINGLE_FUNCTIONS_CASES)
class TestSingleFunctions(ParametrizedTestCase):

    def setParameters(self, code, expected_complexity):
        self.code = dedent(code)
        self.expected_complexity = expected_complexity

    def testComplexityVisitor(self):
        visitor = ComplexityVisitor.from_code(self.code)
        self.assertEqual(len(visitor.functions), 1)
        self.assertEqual((visitor.complexity, visitor.functions[0].complexity),
                         self.expected_complexity)


@parametrized(*FUNCTIONS_CASES)
class TestFunctions(ParametrizedTestCase):

    def setParameters(self, code, expected_complexity):
        self.code = dedent(code)
        self.expected_complexity = expected_complexity

    def testComplexityVisitor(self):
        visitor = ComplexityVisitor.from_code(self.code)
        self.assertEqual(len(visitor.functions), len(self.expected_complexity))
        self.assertEqual(tuple(map(GET_COMPLEXITY, visitor.functions)),
                         self.expected_complexity)


@parametrized(*CLASSES_CASES)
class TestClasses(ParametrizedTestCase):

    def setParameters(self, code, expected_complexity):
        self.code = dedent(code)
        self.total_class_complexity = expected_complexity[0]
        self.methods_complexity = expected_complexity[1:]

    def testComplexityVisitor(self):
        visitor = ComplexityVisitor.from_code(self.code)
        self.assertEqual(len(visitor.classes), 1)
        self.assertEqual(len(visitor.functions), 0)
        cls = visitor.classes[0]
        self.assertEqual(cls.real_complexity, self.total_class_complexity)
        self.assertEqual(tuple(map(GET_COMPLEXITY, cls.methods)),
                         self.methods_complexity)


if __name__ == '__main__':
    import unittest
    unittest.main()
