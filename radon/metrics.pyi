import ast as ast
import collections as collections
import math as math
import typing as _typing

from _typeshed import ReadableBuffer

from radon.raw import analyze as analyze
from radon.visitors import ComplexityVisitor as ComplexityVisitor
from radon.visitors import HalsteadVisitor as HalsteadVisitor

_Source = _typing.Union[str, ReadableBuffer]

class HalsteadReport(_typing.NamedTuple):
    h1: int
    h2: int
    N1: int
    N2: int
    vocabulary: int
    length: int
    calculated_length: float
    volume: float
    difficulty: float
    effort: float
    time: float
    bugs: float

class Halstead(_typing.NamedTuple):
    total: HalsteadReport
    functions: _typing.List[
        _typing.Tuple[_typing.Optional[str], HalsteadReport]
    ]

def h_visit(code: _Source) -> Halstead: ...
def h_visit_ast(ast_node: ast.AST) -> Halstead: ...
def halstead_visitor_report(
    visitor: HalsteadVisitor,
) -> HalsteadReport: ...
def mi_compute(
    halstead_volume: float,
    complexity: float,
    sloc: float,
    comments: float,
) -> float: ...
def mi_parameters(
    code: str, count_multi: bool = True
) -> _typing.Tuple[float, int, int, float]: ...
def mi_visit(code: str, multi: bool) -> float: ...
def mi_rank(score: float) -> str: ...
