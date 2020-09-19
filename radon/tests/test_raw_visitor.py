import pytest

from radon.raw import Module, analyze
from radon.raw_visitor import RawVisitor
from radon.tests import test_raw

# only testing cases with functions, and remove test with trailing
# comment since this is not in the function scope.
reuseable_tests = test_raw.ANALYZE_CASES[9:13] + test_raw.ANALYZE_CASES[14:]
@pytest.mark.parametrize('code, expected', reuseable_tests)
def test_raw_visitor_functions(code, expected):
    code = test_raw.dedent(code)
    raw_visitor = RawVisitor.from_code(code)
    # only one function in these tests
    raw_result = raw_visitor.functions[0]
    # exclude the details about function name, lineno, etc. for now
    formated_result = Module(*raw_result[7:])
    assert formated_result == Module(*expected), '\n result: \
        {}\n expected: {}'.format(formated_result, Module(*expected))
    assert formated_result.loc == formated_result.blank \
                                    + formated_result.sloc \
                                    + formated_result.single_comments \
                                    + formated_result.multi

# @pytest.mark.parametrize('code,expected', ANALYZE_CASES)
# def test_analyze(code, expected):
#     code = dedent(code)

#     try:
#         len(expected)
#     except:
#         with pytest.raises(expected):
#             analyze(code)
#     else:
#         result = analyze(code)
#         assert result == Module(*expected)
#         assert result.loc == result.blank + result.sloc + result.single_comments + result.multi