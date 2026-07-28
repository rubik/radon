import ast as _ast
import math as math
import typing as _typing

import typing_extensions as _typing_extensions
from _typeshed import ReadableBuffer, SupportsRichComparison

import radon.visitors as _visitors
from radon.visitors import GET_COMPLEXITY as GET_COMPLEXITY
from radon.visitors import ComplexityVisitor as ComplexityVisitor
from radon.visitors import code2ast as code2ast

_Block = _typing.Union[_visitors.Function, _visitors.Class]
_BlockT = _typing.TypeVar("_BlockT", bound=_Block)
_Source = _typing.Union[str, ReadableBuffer]

SCORE: _typing.Callable[[_Block], int]
LINES: _typing.Callable[[_Block], int]
ALPHA: _typing.Callable[[_Block], str]

class _ComplexityOptions(_typing_extensions.TypedDict, total=False):
    to_method: bool
    classname: _typing.Optional[str]
    off: bool
    no_assert: bool

def cc_rank(cc: float) -> str: ...
def average_complexity(
    blocks: _typing.Sequence[_Block],
) -> float: ...
def sorted_results(
    blocks: _typing.Iterable[_BlockT],
    order: _typing.Callable[[_BlockT], SupportsRichComparison] = SCORE,
) -> _typing.List[_BlockT]: ...
def add_inner_blocks(
    blocks: _typing.List[_BlockT],
) -> _typing.List[_Block]: ...
def cc_visit(
    code: _Source, **kwargs: _typing_extensions.Unpack[_ComplexityOptions]
) -> _typing.List[_Block]: ...
def cc_visit_ast(
    ast_node: _ast.AST, **kwargs: _typing_extensions.Unpack[_ComplexityOptions]
) -> _typing.List[_Block]: ...
