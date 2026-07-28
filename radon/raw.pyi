import collections as collections
import io as io
import operator as operator
import tokenize as tokenize
import typing as _typing

__all__ = [
    "OP",
    "COMMENT",
    "TOKEN_NUMBER",
    "NL",
    "NEWLINE",
    "EM",
    "Module",
    "_generate",
    "_fewer_tokens",
    "_find",
    "_logical",
    "analyze",
]

COMMENT: int
OP: int
NL: int
NEWLINE: int
EM: int
TOKEN_NUMBER: _typing.Callable[[tokenize.TokenInfo], int]

class Module(_typing.NamedTuple):
    loc: int
    lloc: int
    sloc: int
    comments: int
    multi: int
    blank: int
    single_comments: int

def _generate(code: str) -> _typing.List[tokenize.TokenInfo]: ...
def _fewer_tokens(
    tokens: _typing.Iterable[tokenize.TokenInfo],
    remove: _typing.Container[int],
) -> _typing.Iterator[tokenize.TokenInfo]: ...
def _find(
    tokens: _typing.Sequence[tokenize.TokenInfo],
    token: int,
    value: str,
) -> int: ...
def _split_tokens(
    tokens: _typing.Iterable[tokenize.TokenInfo],
    token: int,
    value: str,
) -> _typing.List[_typing.List[tokenize.TokenInfo]]: ...
def _get_all_tokens(
    line: str, lines: _typing.Iterator[str]
) -> _typing.Tuple[_typing.List[tokenize.TokenInfo], _typing.List[str]]: ...
def _logical(
    tokens: _typing.Sequence[tokenize.TokenInfo],
) -> int: ...
def is_single_token(
    token_number: int,
    tokens: _typing.Sequence[tokenize.TokenInfo],
) -> bool: ...
def analyze(source: str) -> Module: ...
