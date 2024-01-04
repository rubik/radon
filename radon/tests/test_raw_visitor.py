import asttokens
import asttokens.util
import pytest

import radon.raw_visitor
from radon.raw import Module
from radon.tests import test_raw

EXTRA_CASES = [
    (
        r'''if 0:
    def something():
        pass
    #Comment
# Ignored comment
    ''',
        (3, 2, 2, 1, 0, 0, 1),  # Expected values for the function node
    ),
]

CASES = test_raw.VISITOR_CASES + test_raw.MAIN_CASES + EXTRA_CASES


@pytest.mark.parametrize("code, expected", CASES)
def test_raw_visitor(code, expected):
    code = test_raw.dedent(code)
    try:
        len(expected)
    except:
        with pytest.raises(expected):
            radon.raw_visitor.RawVisitor.from_code(code)
    else:
        raw_visitor = radon.raw_visitor.RawVisitor.from_code(code)
        # Handle only one function in these tests
        if len(raw_visitor.functions) == 1:
            raw_result = raw_visitor.functions[0]
            # exclude the details about function name, lineno, etc. for now
            formatted_result = Module(*raw_result[7:])
        elif len(raw_visitor.classes) == 1:
            raw_result = raw_visitor.classes[0]
            formatted_result = Module(*raw_result[6:])
        else:
            formatted_result = raw_visitor.module
        assert formatted_result == Module(
            *expected
        ), f"\
            \n input code: {code}\
            \n result: {formatted_result} \
            \n expected: {Module(*expected)}"

        expected_loc = (
            formatted_result.blank
            + formatted_result.sloc
            + formatted_result.single_comments
            + formatted_result.multi
        )
        assert formatted_result.loc == expected_loc


module = """
import foo  # Inline comment


class Something(foo.Nothing):
    '''Class doc.'''

    def method(self, thing):
        '''Method doc.'''
        print(thing)
        # Line comment
        self.thing = thing
        # Trailing comment


def function(parameter):
    return parameter
"""


def test_raw_visitor_module():
    code = test_raw.dedent(module)
    visitor = radon.raw_visitor.RawVisitor.from_code(code)
    ast_visitor = radon.raw_visitor.RawVisitor.from_ast(asttokens.ASTTokens(code, parse=True).tree)
    assert visitor.blocks == ast_visitor.blocks
    first_block = visitor.blocks[0][1]
    assert visitor.module == first_block
    assert isinstance(first_block, Module)
    for _name, block in visitor.blocks:
        assert isinstance(block, (Module, radon.raw_visitor.RawClassMetrics, radon.raw_visitor.RawFunctionMetrics))
    blocks = dict(visitor.blocks)
    assert "__ModuleMetrics__" in blocks
    assert blocks["__ModuleMetrics__"] is first_block
    assert blocks["__ModuleMetrics__"].loc == len(code.splitlines())
    assert blocks["__ModuleMetrics__"].comments == 3
    assert "Something" in blocks
    assert blocks["Something"].methods[0].name == "method"
    assert blocks["Something"].methods[0].classname == "Something"
    assert blocks["Something"].methods[0].is_method is True
    assert "Something.method" in blocks
    assert blocks["Something"].methods[0] == blocks["Something.method"]
    assert blocks["Something.method"].comments == 2
    assert blocks["Something.method"].single_comments == 3
    assert "function" in blocks
    assert blocks["function"].name == "function"
    assert blocks["function"].loc == 2
    assert blocks["function"].is_method is False


def test_get_trailing_comments():
    code = test_raw.dedent(module)
    atok = asttokens.ASTTokens(code, parse=True)
    for node in asttokens.util.walk(atok.tree):
        if hasattr(node, "name") and node.name == "method":
            break
    segment = atok.get_text(node)
    trailing = radon.raw_visitor.get_trailing_comments(atok, node, segment)
    assert trailing not in segment
    assert "# Trailing comment" in trailing
    assert (segment + trailing) in code
