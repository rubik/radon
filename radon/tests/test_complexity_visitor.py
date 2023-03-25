import sys
import textwrap

import pytest

from radon.visitors import *

dedent = lambda code: textwrap.dedent(code).strip()


SIMPLE_BLOCKS = [
    (
        '''
     if a: pass
     ''',
        2,
        {},
    ),
    (
        '''
     if a: pass
     else: pass
     ''',
        2,
        {},
    ),
    (
        '''
     if a: pass
     elif b: pass
     ''',
        3,
        {},
    ),
    (
        '''
     if a: pass
     elif b: pass
     else: pass
     ''',
        3,
        {},
    ),
    (
        '''
    if a and b: pass
    ''',
        3,
        {},
    ),
    (
        '''
    if a and b: pass
    else: pass
    ''',
        3,
        {},
    ),
    (
        '''
     if a and b: pass
     elif c and d: pass
     else: pass
     ''',
        5,
        {},
    ),
    (
        '''
     if a and b or c and d: pass
     else: pass
     ''',
        5,
        {},
    ),
    (
        '''
     if a and b or c: pass
     else: pass
     ''',
        4,
        {},
    ),
    (
        '''
     for x in range(10): print(x)
     ''',
        2,
        {},
    ),
    (
        '''
     for x in xrange(10): print(x)
     else: pass
     ''',
        3,
        {},
    ),
    (
        '''
     while a < 4: pass
     ''',
        2,
        {},
    ),
    (
        '''
     while a < 4: pass
     else: pass
     ''',
        3,
        {},
    ),
    (
        '''
     while a < 4 and b < 42: pass
     ''',
        3,
        {},
    ),
    (
        '''
     while a and b or c < 10: pass
     else: pass
     ''',
        5,
        {},
    ),
    # With and async-with statements no longer count towards CC, see #123
    (
        '''
     with open('raw.py') as fobj: print(fobj.read())
     ''',
        1,
        {},
    ),
    (
        '''
     [i for i in range(4)]
     ''',
        2,
        {},
    ),
    (
        '''
     [i for i in range(4) if i&1]
     ''',
        3,
        {},
    ),
    (
        '''
     (i for i in range(4))
     ''',
        2,
        {},
    ),
    (
        '''
     (i for i in range(4) if i&1)
     ''',
        3,
        {},
    ),
    (
        '''
     [i for i in range(42) if sum(k ** 2 for k in divisors(i)) & 1]
     ''',
        4,
        {},
    ),
    (
        '''
     try: raise TypeError
     except TypeError: pass
     ''',
        2,
        {},
    ),
    (
        '''
     try: raise TypeError
     except TypeError: pass
     else: pass
     ''',
        3,
        {},
    ),
    (
        '''
     try: raise TypeError
     finally: pass
     ''',
        1,
        {},
    ),
    (
        '''
     try: raise TypeError
     except TypeError: pass
     finally: pass
     ''',
        2,
        {},
    ),
    (
        '''
     try: raise TypeError
     except TypeError: pass
     else: pass
     finally: pass
     ''',
        3,
        {},
    ),
    (
        '''
     try: raise TypeError
     except TypeError: pass
     else:
        pass
        pass
     finally: pass
     ''',
        3,
        {},
    ),
    # Lambda are not counted anymore as per #68
    (
        '''
     k = lambda a, b: k(b, a)
     ''',
        1,
        {},
    ),
    (
        '''
     k = lambda a, b, c: c if a else b
     ''',
        2,
        {},
    ),
    (
        '''
     v = a if b else c
     ''',
        2,
        {},
    ),
    (
        '''
     v = a if sum(i for i in xrange(c)) < 10 else c
     ''',
        3,
        {},
    ),
    (
        '''
     sum(i for i in range(12) for z in range(i ** 2) if i * z & 1)
     ''',
        4,
        {},
    ),
    (
        '''
     sum(i for i in range(10) if i >= 2 and val and val2 or val3)
     ''',
        6,
        {},
    ),
    (
        '''
     for i in range(10):
         print(i)
     else:
         print('wah')
         print('really not found')
         print(3)
     ''',
        3,
        {},
    ),
    (
        '''
     while True:
         print(1)
     else:
         print(2)
         print(1)
         print(0)
         print(-1)
     ''',
        3,
        {},
    ),
    (
        '''
     assert i < 0
     ''',
        2,
        {},
    ),
    (
        '''
     assert i < 0, "Fail"
     ''',
        2,
        {},
    ),
    (
        '''
     assert i < 0
     ''',
        1,
        {'no_assert': True},
    ),
    (
        '''
     def f():
        assert 10 > 20
     ''',
        1,
        {'no_assert': True},
    ),
    (
        '''
     class TestYo(object):
        def test_yo(self):
            assert self.n > 4
     ''',
        1,
        {'no_assert': True},
    ),
]


# These run only if Python version is >= 2.7
ADDITIONAL_BLOCKS = [
    (
        '''
     {i for i in range(4)}
     ''',
        2,
        {},
    ),
    (
        '''
     {i for i in range(4) if i&1}
     ''',
        3,
        {},
    ),
    (
        '''
     {i:i**4 for i in range(4)}
     ''',
        2,
        {},
    ),
    (
        '''
     {i:i**4 for i in range(4) if i&1}
     ''',
        3,
        {},
    ),
]

# The match statement was introduced in Python 3.10
MATCH_STATEMENT_BLOCKS = [
    (
        '''
     match a:
         case 1: pass
     ''',
        2,
        {},
    ),
    (
        '''
     match a:
         case 1: pass
         case _: pass
     ''',
        2,
        {},
    ),
    (
        '''
     match a:
         case 1: pass
         case 2: pass
     ''',
        3,
        {},
    ),
    (
        '''
     match a:
         case 1: pass
         case 2: pass
         case _: pass
     ''',
        3,
        {},
    ),
]

BLOCKS = SIMPLE_BLOCKS[:]
if sys.version_info[:2] >= (2, 7):
    BLOCKS.extend(ADDITIONAL_BLOCKS)
if sys.version_info[:2] >= (3, 10):
    BLOCKS.extend(MATCH_STATEMENT_BLOCKS)


@pytest.mark.parametrize('code,expected,kwargs', BLOCKS)
def test_visitor_simple(code, expected, kwargs):
    visitor = ComplexityVisitor.from_code(dedent(code), **kwargs)
    assert visitor.complexity == expected


SINGLE_FUNCTIONS_CASES = [
    (
        '''
     def f(a, b, c):
        if a and b == 4:
            return c ** c
        elif a and not c:
            return sum(i for i in range(41) if i&1)
        return a + b
     ''',
        (1, 7),
    ),
    (
        '''
     if a and not b: pass
     elif b or c: pass
     else: pass

     for i in range(4):
        print(i)

     def g(a, b):
        while a < b:
            b, a = a **2, b ** 2
        return b
     ''',
        (6, 2),
    ),
    (
        '''
     def f(a, b):
        while a**b:
            a, b = b, a * (b - 1)
            if a and b:
                b = 0
            else:
                b = 1
        return sum(i for i in range(b))
     ''',
        (1, 5),
    ),
]

if sys.version_info[:2] >= (3, 5):
    # With and async-with statements no longer count towards CC, see #123
    SINGLE_FUNCTIONS_CASES.append(
        (
            '''
         async def f(a, b):
            async with open('blabla.log', 'w') as f:
                async for i in range(100):
                    f.write(str(i) + '\\n')
         ''',
            (1, 2),
        ),
    )


@pytest.mark.parametrize('code,expected', SINGLE_FUNCTIONS_CASES)
def test_visitor_single_functions(code, expected):
    visitor = ComplexityVisitor.from_code(dedent(code))
    assert len(visitor.functions) == 1
    assert (visitor.complexity, visitor.functions[0].complexity) == expected


FUNCTIONS_CASES = [
    # With and async-with statements no longer count towards CC, see #123
    (
        '''
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
     ''',
        (2, 5, 1),
    ),
    (
        '''
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
     ''',
        (5, 9),
    ),
]


@pytest.mark.parametrize('code,expected', FUNCTIONS_CASES)
def test_visitor_functions(code, expected):
    visitor = ComplexityVisitor.from_code(dedent(code))
    assert len(visitor.functions) == len(expected)
    assert tuple(map(GET_COMPLEXITY, visitor.functions)) == expected


CLASSES_CASES = [
    (
        '''
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
     ''',
        (8, 4, 3),
    ),
    (
        '''
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
     ''',
        (7, 1, 3),
    ),
]


@pytest.mark.parametrize('code,expected', CLASSES_CASES)
def test_visitor_classes(code, expected):
    total_class_complexity = expected[0]
    methods_complexity = expected[1:]
    visitor = ComplexityVisitor.from_code(dedent(code))
    assert len(visitor.classes) == 1
    assert len(visitor.functions) == 0
    cls = visitor.classes[0]
    assert cls.real_complexity == total_class_complexity
    assert tuple(map(GET_COMPLEXITY, cls.methods)) == methods_complexity


GENERAL_CASES = [
    (
        '''
     if a and b:
         print
     else:
         print
     a = sum(i for i in range(1000) if i % 3 == 0 and i % 5 == 0)

     def f(n):
         def inner(n):
             return n ** 2

         if n == 0:
             return 1
         elif n == 1:
             return n
         elif n < 5:
             return (n - 1) ** 2
         return n * pow(inner(n), f(n - 1), n - 3)
     ''',
        (6, 3, 0, 9),
    ),
    (
        '''
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
         def inner(n):
             return n ** 2
         if a < b:
             b, a = a, inner(b)
         return a, b
     ''',
        (3, 1, 3, 7),
    ),
    (
        '''
     class f(object):
         class inner(object):
             pass
     ''',
        (1, 0, 0, 1),
    ),
]


@pytest.mark.parametrize('code,expected', GENERAL_CASES)
def test_visitor_module(code, expected):
    (
        module_complexity,
        functions_complexity,
        classes_complexity,
        total_complexity,
    ) = expected

    visitor = ComplexityVisitor.from_code(dedent(code))
    assert visitor.complexity, module_complexity
    assert visitor.functions_complexity == functions_complexity
    assert visitor.classes_complexity == classes_complexity
    assert visitor.total_complexity == total_complexity


CLOSURES_CASES = [
    (
        '''
     def f(n):
         def g(l):
             return l ** 4
         def h(i):
             return i ** 5 + 1 if i & 1 else 2
         return sum(g(u + 4) / float(h(u)) for u in range(2, n))
     ''',
        ('g', 'h'),
        (1, 2, 2),
    ),
    (
        '''
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
     ''',
        ('aux',),
        (2, 1),
    ),
]


@pytest.mark.parametrize('code,closure_names,expected', CLOSURES_CASES)
def test_visitor_closures(code, closure_names, expected):
    visitor = ComplexityVisitor.from_code(dedent(code))
    func = visitor.functions[0]
    closure_names = closure_names
    expected_cs_cc = expected[:-1]
    expected_total_cc = expected[-1]

    assert len(visitor.functions) == 1

    names = tuple(cs.name for cs in func.closures)
    assert names == closure_names

    cs_complexity = tuple(cs.complexity for cs in func.closures)
    assert cs_complexity == expected_cs_cc
    assert func.complexity == expected_total_cc

    # There was a bug for which `blocks` increased while it got accessed
    v = visitor
    assert v.blocks == v.blocks == v.blocks


CONTAINERS_CASES = [
    (
        ('func', 12, 0, 18, False, None, [], 5),
        ('F', 'func', 'F 12:0->18 func - 5'),
    ),
    (
        ('meth', 12, 0, 21, True, 'cls', [], 5),
        ('M', 'cls.meth', 'M 12:0->21 cls.meth - 5'),
    ),
    (('cls', 12, 0, 15, [], [], 5), ('C', 'cls', 'C 12:0->15 cls - 5')),
    (
        ('cls', 12, 0, 19, [object, object, object, object], [], 30),
        ('C', 'cls', 'C 12:0->19 cls - 8'),
    ),
]


@pytest.mark.parametrize('values,expected', CONTAINERS_CASES)
def test_visitor_containers(values, expected):
    expected_letter, expected_name, expected_str = expected

    cls = Function if len(values) == 8 else Class
    obj = cls(*values)
    assert obj.letter == expected_letter
    assert obj.fullname == expected_name
    assert str(obj) == expected_str
