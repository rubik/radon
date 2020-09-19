import sys

import pytest

from radon.raw import Module
from radon.tests import test_raw

# we expect an ImportError when python <3.8
try:
    from radon.raw_visitor import RawVisitor

    IMPORT_ERROR = False
except ImportError:
    IMPORT_ERROR = True

min_py_version = pytest.mark.xfail(
    IMPORT_ERROR and sys.version_info < (3, 8),
    reason="raw_visitor requires python >=3.8",
)


@min_py_version
@pytest.mark.parametrize("code, expected", test_raw.VISITOR_CASES)
def test_raw_visitor_functions(code, expected):
    code = test_raw.dedent(code)
    raw_visitor = RawVisitor.from_code(code)
    # only one function in these tests
    raw_result = raw_visitor.functions[0]
    # exclude the details about function name, lineno, etc. for now
    formated_result = Module(*raw_result[7:])
    assert formated_result == Module(
        *expected
    ), f"\
        \n input code: {code}\
        \n result: {formated_result} \
        \n expected: {Module(*expected)}"

    expected_loc = (
        formated_result.blank
        + formated_result.sloc
        + formated_result.single_comments
        + formated_result.multi
    )
    assert formated_result.loc == expected_loc
