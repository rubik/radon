import textwrap
from paramunittest import *
from radon.visitors import HalsteadVisitor


dedent = lambda code: textwrap.dedent(code).strip()


SIMPLE_BLOCKS = [
    ('''
     if a and b: pass
     ''', (1, 2, 1, 2)),

    ('''
     if a and b: pass
     elif b or c: pass
     ''', (2, 4, 2, 3)),

    ('''
     if a and b: pass
     elif b and c: pass
     ''', (2, 4, 1, 3)),

    ('''
     a = b * c
     ''', (1, 2, 1, 2)),

    ('''
     b = -x
     ''', (1, 1, 1, 1)),

    ('''
     a = -x
     c = -x
     ''', (2, 2, 1, 1)),

    ('''
     a = -x
     b = +x
     ''', (2, 2, 2, 1)),

    ('''
     a += 3
     b += 4
     c *= 3
     ''', (3, 6, 2, 5)),

    ('''
     a = 2
     b = 3
     a *= b

     def f():
         b = 2
         b += 4
     ''', (2, 4, 2, 4)),

    ('''
     a = b < 4
     c = i <= 45 >= d
     k = 4 < 2
     ''', (4, 7, 3, 6)),
]


@parametrized(*SIMPLE_BLOCKS)
class TestHalsteadVisitor(ParametrizedTestCase):

    def setParameters(self, code, expected_result):
        self.code = dedent(code)
        self.expected_result = expected_result

    def test_HalsteadVisitor(self):
        visitor = HalsteadVisitor.from_code(self.code)
        result = visitor.operators, visitor.operands, \
            visitor.distinct_operators, visitor.distinct_operands
        self.assertEqual(result, self.expected_result)
