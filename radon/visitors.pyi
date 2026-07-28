import ast as ast
import collections as collections
import operator as operator
import typing as _typing

import typing_extensions as _typing_extensions
from _typeshed import ReadableBuffer

class BaseFunc(_typing.NamedTuple):
    name: str
    lineno: int
    col_offset: int
    endline: int
    is_method: bool
    classname: _typing.Optional[str]
    closures: _typing.List["Function"]
    complexity: int

class Function(BaseFunc):
    @property
    def letter(self) -> str: ...
    @property
    def fullname(self) -> str: ...
    def __str__(self) -> str: ...

class BaseClass(_typing.NamedTuple):
    name: str
    lineno: int
    col_offset: int
    endline: int
    methods: _typing.List[Function]
    inner_classes: _typing.List["Class"]
    real_complexity: int

class Class(BaseClass):
    letter: _typing.ClassVar[str]
    @property
    def fullname(self) -> str: ...
    @property
    def complexity(self) -> int: ...
    def __str__(self) -> str: ...

_Block = _typing.Union[Function, Class]
_Source = _typing.Union[str, ReadableBuffer]

class _HasComplexity(_typing_extensions.Protocol):
    @property
    def complexity(self) -> int: ...

class _HasRealComplexity(_typing_extensions.Protocol):
    @property
    def real_complexity(self) -> int: ...

class _HasNames(_typing_extensions.Protocol):
    @property
    def name(self) -> str: ...
    @property
    def asname(self) -> _typing.Optional[str]: ...

class _HasEndLine(_typing_extensions.Protocol):
    @property
    def endline(self) -> int: ...

class _GetComplexity(_typing_extensions.Protocol):
    def __call__(self, __obj: _HasComplexity) -> int: ...

class _GetRealComplexity(_typing_extensions.Protocol):
    def __call__(self, __obj: _HasRealComplexity) -> int: ...

class _GetNames(_typing_extensions.Protocol):
    def __call__(
        self, __obj: _HasNames
    ) -> _typing.Tuple[str, _typing.Optional[str]]: ...

class _GetEndLine(_typing_extensions.Protocol):
    def __call__(self, __obj: _HasEndLine) -> int: ...

GET_COMPLEXITY: _GetComplexity
GET_REAL_COMPLEXITY: _GetRealComplexity
NAMES_GETTER: _GetNames
GET_ENDLINE: _GetEndLine

def code2ast(source: _Source) -> ast.Module: ...

_CodeVisitorT = _typing.TypeVar("_CodeVisitorT", bound="CodeVisitor")

class CodeVisitor(ast.NodeVisitor):
    @staticmethod
    def get_name(obj: object) -> str: ...
    @classmethod
    def from_code(
        cls: _typing.Type[_CodeVisitorT],
        code: _Source,
        **kwargs: object,
    ) -> _CodeVisitorT: ...
    @classmethod
    def from_ast(
        cls: _typing.Type[_CodeVisitorT],
        ast_node: ast.AST,
        **kwargs: object,
    ) -> _CodeVisitorT: ...

class ComplexityVisitor(CodeVisitor):
    off: bool
    complexity: int
    functions: _typing.List[Function]
    classes: _typing.List[Class]
    to_method: bool
    classname: _typing.Optional[str]
    no_assert: bool
    _max_line: float

    def __init__(
        self,
        to_method: bool = False,
        classname: _typing.Optional[str] = None,
        off: bool = True,
        no_assert: bool = False,
    ) -> None: ...
    @property
    def functions_complexity(self) -> int: ...
    @property
    def classes_complexity(self) -> int: ...
    @property
    def total_complexity(self) -> int: ...
    @property
    def blocks(self) -> _typing.List[_Block]: ...
    @property
    def max_line(self) -> float: ...
    @max_line.setter
    def max_line(self, value: float) -> None: ...
    def generic_visit(self, node: ast.AST) -> None: ...
    def visit_Assert(self, node: ast.Assert) -> None: ...
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None: ...
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None: ...
    def visit_ClassDef(self, node: ast.ClassDef) -> None: ...

_DispatchParameters = _typing_extensions.ParamSpec("_DispatchParameters")
_DispatchResult = _typing.Tuple[
    int,
    int,
    _typing.Iterable[object],
    _typing.Iterable[object],
]

class _BoundDispatch(_typing_extensions.Protocol):
    def __call__(
        self,
    ) -> _typing.Callable[["HalsteadVisitor", ast.AST], None]: ...

class _DispatchDecorator(_typing_extensions.Protocol):
    def __call__(
        self,
        method: _typing.Callable[_DispatchParameters, _DispatchResult],
    ) -> _typing.Callable[_DispatchParameters, None]: ...

class _Dispatch(_typing_extensions.Protocol):
    @_typing.overload
    def __get__(
        self,
        __instance: None,
        __owner: _typing.Type[object],
    ) -> _DispatchDecorator: ...
    @_typing.overload
    def __get__(
        self,
        __instance: "HalsteadVisitor",
        __owner: _typing.Optional[_typing.Type["HalsteadVisitor"]] = ...,
    ) -> _BoundDispatch: ...

class HalsteadVisitor(CodeVisitor):
    types: _typing.ClassVar[_typing.Dict[str, str]]
    operators_seen: _typing.Set[str]
    operands_seen: _typing.Set[_typing.Tuple[_typing.Optional[str], object]]
    operators: int
    operands: int
    context: _typing.Optional[str]
    function_visitors: _typing.List["HalsteadVisitor"]
    dispatch: _Dispatch

    def __init__(self, context: _typing.Optional[str] = None) -> None: ...
    @property
    def distinct_operators(self) -> int: ...
    @property
    def distinct_operands(self) -> int: ...
    def visit_BinOp(self, node: ast.BinOp) -> None: ...
    def visit_UnaryOp(self, node: ast.UnaryOp) -> None: ...
    def visit_BoolOp(self, node: ast.BoolOp) -> None: ...
    def visit_AugAssign(self, node: ast.AugAssign) -> None: ...
    def visit_Compare(self, node: ast.Compare) -> None: ...
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None: ...
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None: ...
