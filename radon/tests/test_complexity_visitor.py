import sys
import textwrap
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from paramunittest import *
from radon.visitors import *


dedent = lambda code: textwrap.dedent(code).strip()


SIMPLE_BLOCKS = [
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
     ''', 1),

    ('''
     try: raise TypeError
     except TypeError: pass
     finally: pass
     ''', 2),

    ('''
     try: raise TypeError
     except TypeError: pass
     else: pass
     finally: pass
     ''', 3),

    ('''
     k = lambda a, b: k(b, a)
     ''', 2),

    ('''
     v = a if b else c
     ''', 2),

    ('''
     v = a if sum(i for i in xrange(c)) < 10 else c
     ''', 3),

    ('''
     sum(i for i in range(12) for z in range(i ** 2) if i * z & 1)
     ''', 4),

    ('''
     sum(i for i in range(10) if i >= 2 and val and val2 or val3)
     ''', 6),

    ('''
     assert i < 0
     ''', 2),

    ('''
     assert i < 0, "Fail"
     ''', 2),
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

BLOCKS = SIMPLE_BLOCKS[:]
if sys.version_info[:2] >= (2, 7):
    BLOCKS.extend(ADDITIONAL_BLOCKS)

@parametrized(*BLOCKS)
class TestBlocks(ParametrizedTestCase):
    '''Test blocks.'''

    def setParameters(self, code, expected_complexity):
        self.code = dedent(code)
        self.expected_complexity = expected_complexity

    def testComplexityVisitor(self):
        visitor = ComplexityVisitor.from_code(self.code)
        self.assertEqual(visitor.complexity, self.expected_complexity)



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


GENERAL_CASES = [
    ('''
     if a and b:
         print
     else:
         print
     a = sum(i for i in range(1000) if i % 3 == 0 and i % 5 == 0)

     def f(n):
         if n == 0:
             return 1
         elif n == 1:
             return n
         elif n < 5:
             return (n - 1) ** 2
         return n * pow(n, f(n - 1), n - 3)
     ''', (6, 3, 0, 9)),

    ('''
     try:
         1 / 0
     except ZeroDivisonError:
         print
     except TypeError:
         pass

     class J(object):

         def aux(self, w):
             if w == 0:
                 return 0
             return w - 1 + sum(self.aux(w - 3 - i) for i in range(2))

     def f(a, b):
         if a < b:
             b, a = a, b
         return a, b
     ''', (3, 1, 2, 6)),
]


@parametrized(*GENERAL_CASES)
class TestModules(ParametrizedTestCase):

    def setParameters(self, code, expected_complexity):
        self.code = dedent(code)
        self.module_complexity, self.functions_complexity, \
            self.classes_complexity, \
            self.total_complexity = expected_complexity

    def testModule(self):
        visitor = ComplexityVisitor.from_code(self.code)
        self.assertEqual(visitor.complexity, self.module_complexity)
        self.assertEqual(visitor.functions_complexity,
                         self.functions_complexity)
        self.assertEqual(visitor.classes_complexity, self.classes_complexity)
        self.assertEqual(visitor.total_complexity, self.total_complexity)


CLOJURES_CASES = [
    ('''
     def f(n):
         def g(l):
             return l ** 4
         def h(i):
             return i ** 5 + 1 if i & 1 else 2
         return sum(g(u + 4) / float(h(u)) for u in range(2, n))
     ''', ('g', 'h'), (1, 2, 3)),

    ('''
     # will it work? :D
     def memoize(func):
         cache = {}
         def aux(*args, **kwargs):
             key = (args, kwargs)
             if key in cache:
                 return cache[key]
             cache[key] = res = func(*args, **kwargs)
             return res
         return aux
     ''', ('aux',), (2, 2)),
]


@parametrized(*CLOJURES_CASES)
class TestClojures(ParametrizedTestCase):

    def setParameters(self, code, clojure_names, expected_cc):
        self.visitor = ComplexityVisitor.from_code(dedent(code))
        self.func = self.visitor.functions[0]
        self.clojure_names = clojure_names
        self.expected_cj_cc = expected_cc[:-1]
        self.expected_total_cc = expected_cc[-1]

    def testOneFunction(self):
        self.assertEqual(len(self.visitor.functions), 1)

    def testClojureNames(self):
        names = tuple(cj.name for cj in self.func.clojures)
        self.assertEqual(names, self.clojure_names)

    def testClojuresComplexity(self):
        cj_complexity = tuple(cj.complexity for cj in self.func.clojures)
        self.assertEqual(cj_complexity, self.expected_cj_cc)

    def testTotalComplexity(self):
        self.assertEqual(self.func.complexity, self.expected_total_cc)


CONTAINERS_CASES = [
    (('func', 12, 0, False, None, [], 5),
     ('F', 'func', 'F 12:0 func - 5')),

    (('meth', 12, 0, True, 'cls', [], 5),
     ('M', 'cls.meth', 'M 12:0 cls.meth - 5')),

    (('cls', 12, 0, [], 5),
     ('C', 'cls', 'C 12:0 cls - 5')),

    (('cls', 12, 0, [object, object, object, object], 30),
     ('C', 'cls', 'C 12:0 cls - 8')),
]


@parametrized(*CONTAINERS_CASES)
class TestContainers(ParametrizedTestCase):

    def setParameters(self, values, expected):
        self.values = values
        self.expected_letter = expected[0]
        self.expected_name = expected[1]
        self.expected_str = expected[2]

    def testContainers(self):
        cls = Function if len(self.values) == 7 else Class
        obj = cls(*self.values)
        self.assertEqual(obj.letter, self.expected_letter)
        self.assertEqual(obj.fullname, self.expected_name)
        self.assertEqual(str(obj), self.expected_str)


if __name__ == '__main__':
    unittest.main()
