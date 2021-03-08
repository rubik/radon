import sys
import textwrap

import pytest

from radon.visitors import HalsteadVisitor

dedent = lambda code: textwrap.dedent(code).strip()


SIMPLE_BLOCKS = [
    (
        '''
     if a and b: pass
     ''',
        (1, 2, 1, 2),
    ),
    (
        '''
     if a and b: pass
     elif b or c: pass
     ''',
        (2, 4, 2, 3),
    ),
    (
        '''
     if a and b: pass
     elif b and c: pass
     ''',
        (2, 4, 1, 3),
    ),
    (
        '''
     a = b * c
     ''',
        (1, 2, 1, 2),
    ),
    (
        '''
     b = -x
     ''',
        (1, 1, 1, 1),
    ),
    (
        '''
     a = -x
     c = -x
     ''',
        (2, 2, 1, 1),
    ),
    (
        '''
     a = -x
     b = +x
     ''',
        (2, 2, 2, 1),
    ),
    (
        '''
     a += 3
     b += 4
     c *= 3
     ''',
        (3, 6, 2, 5),
    ),
    (
        '''
     a = 2
     b = 3
     a *= b

     def f():
         b = 2
         b += 4
     ''',
        (2, 4, 2, 4),
    ),
    (
        '''
     a = b < 4
     c = i <= 45 >= d
     k = 4 < 2
     ''',
        (4, 7, 3, 6),
    ),
]

if sys.version_info[:2] >= (3, 5):
    SIMPLE_BLOCKS.append(
        (
            '''
        a = 2
        b = 3
        a *= b

        async def f():
            b = 2
            b += 4
        ''',
            (2, 4, 2, 4),
        ),
    )


@pytest.mark.parametrize('code,expected', SIMPLE_BLOCKS)
def test_visitor(code, expected):
    visitor = HalsteadVisitor.from_code(dedent(code))
    assert expected == (
        visitor.operators,
        visitor.operands,
        visitor.distinct_operators,
        visitor.distinct_operands,
    )
