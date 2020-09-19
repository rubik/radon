from collections import namedtuple
import ast

from radon.metrics import analyze
from radon.visitors import GET_ENDLINE, code2ast
from radon.cli.tools import raw_to_dict

try:
    from ast import get_source_segment
except ImportError:
    raise ImportError("raw_visitor module requires Python >=3.8")


BaseRawFuncMetrics = namedtuple(
    "BaseRawFuncMetrics",
    [
        "name",
        "lineno",
        "col_offset",
        "endline",
        "is_method",
        "classname",
        "closures",
        "loc",
        "lloc",
        "sloc",
        "comments",
        "multi",
        "blank",
        "single_comments",
    ],
)

BaseRawClassMetrics = namedtuple(
    "BaseRawClassMetrics",
    [
        "name",
        "lineno",
        "col_offset",
        "endline",
        "methods",
        "inner_classes",
        "loc",
        "lloc",
        "sloc",
        "comments",
        "multi",
        "blank",
        "single_comments",
    ],
)


class RawFunctionMetrics(BaseRawFuncMetrics):
    """Object represeting a function block."""

    @property
    def letter(self):
        """The letter representing the function. It is `M` if the function is
        actually a method, `F` otherwise.
        """
        return "M" if self.is_method else "F"

    @property
    def fullname(self):
        """The full name of the function. If it is a method, then the full name
        is:
                {class name}.{method name}
        Otherwise it is just the function name.
        """
        if self.classname is None:
            return self.name
        return "{0}.{1}".format(self.classname, self.name)

    def __str__(self):
        """String representation of a function block."""
        return "{0} {1}:{2}->{3} {4} - sloc: {5}".format(
            self.letter,
            self.lineno,
            self.col_offset,
            self.endline,
            self.fullname,
            self.sloc,
        )


class RawClassMetrics(BaseRawClassMetrics):
    """Object representing a class block."""

    letter = "C"

    @property
    def fullname(self):
        """The full name of the class. It is just its name. This attribute
        exists for consistency (see :data:`RawFunctionMetrics.fullname`).
        """
        return self.name

    def __str__(self):
        """String representation of a class block."""
        return "{0} {1}:{2}->{3} {4} - sloc: {5}".format(
            self.letter,
            self.lineno,
            self.col_offset,
            self.endline,
            self.name,
            self.sloc,
        )


class CodeVisitor(ast.NodeVisitor):
    """Base class for every NodeVisitors in `radon.visitors`. It implements a
    couple utility class methods and a static method.
    """

    @staticmethod
    def get_name(obj):
        """Shorthand for ``obj.__class__.__name__``."""
        return obj.__class__.__name__

    @classmethod
    def from_code(cls, code, **kwargs):
        """Instantiate the class from source code (string object). The
        `**kwargs` are directly passed to the `ast.NodeVisitor` constructor.
        """
        cls.code = code
        node = code2ast(code)
        return cls.from_ast(node, **kwargs)

    @classmethod
    def from_ast(cls, ast_node, **kwargs):
        """Instantiate the class from an AST node. The `**kwargs` are
        directly passed to the `ast.NodeVisitor` constructor.
        """
        visitor = cls(**kwargs)
        visitor.visit(ast_node)
        return visitor


class RawVisitor(CodeVisitor):
    """A visitor that keeps track of raw metrics for block of code.

    Metrics are provided for functions, classes and class methods.

    :param to_method: If True, every function is treated as a method. In this
        case the *classname* parameter is used as class name.
    :param classname: Name of parent class.
    :param off: If True, the starting value for the complexity is set to 1,
        otherwise to 0.
    """

    def __init__(self, to_method=False, classname=None):
        self.functions = []
        self.classes = []
        self.to_method = to_method
        self.classname = classname
        self._max_line = float("-inf")

    @property
    def blocks(self):
        """All the blocks visited. These include: all the functions, the
        classes and their methods. The returned list is not sorted.
        """
        blocks = []
        blocks.extend(self.functions)
        for cls in self.classes:
            blocks.append(cls)
            blocks.extend(cls.methods)
        return blocks

    @property
    def max_line(self):
        """The maximum line number among the analyzed lines."""
        return self._max_line

    @max_line.setter
    def max_line(self, value):
        """The maximum line number among the analyzed lines."""
        if value > self._max_line:
            self._max_line = value

    def generic_visit(self, node):
        """Main entry point for the visitor."""
        # Check for a lineno attribute
        if hasattr(node, "lineno"):
            self.max_line = node.lineno

        super(RawVisitor, self).generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Async function definition is the same thing as the synchronous
        one.
        """
        self.visit_FunctionDef(node)

    def get_raw_metrics(self, node):
        # astunparse.unparse() parses triple quote strings
        # a single quote strings.  A single quote string is
        # interpreted as a sloc instead of a multi.
        # source_segement = unparse(node)

        source_segment = get_source_segment(self.code, node)
        raw_metrics = analyze(source_segment)
        raw_metrics_dict = raw_to_dict(raw_metrics)
        self.loc = raw_metrics_dict["loc"]
        self.lloc = raw_metrics_dict["lloc"]
        self.sloc = raw_metrics_dict["sloc"]
        self.comments = raw_metrics_dict["comments"]
        self.multi = raw_metrics_dict["multi"]
        self.blank = raw_metrics_dict["blank"]
        self.single_comments = raw_metrics_dict["single_comments"]

    def visit_FunctionDef(self, node):
        """When visiting functions a new visitor is created to recursively
        analyze the function's body.
        """
        closures = []

        for child in node.body:
            visitor = RawVisitor()
            visitor.visit(child)
            closures.extend(visitor.functions)

        self.get_raw_metrics(node)
        func_metrics = RawFunctionMetrics(
            node.name,
            node.lineno,
            node.col_offset,
            max(node.lineno, visitor.max_line),
            self.to_method,
            self.classname,
            closures,
            self.loc,
            self.lloc,
            self.sloc,
            self.comments,
            self.multi,
            self.blank,
            self.single_comments,
        )

        self.functions.append(func_metrics)

    def visit_ClassDef(self, node):
        """When visiting classes a new visitor is created to recursively
        analyze the class' body and methods.
        """
        methods = []
        classname = node.name
        visitors_max_lines = [node.lineno]
        inner_classes = []
        for child in node.body:
            visitor = RawVisitor(
                True,
                classname,
            )
            visitor.visit(child)
            methods.extend(visitor.functions)
            visitors_max_lines.append(visitor.max_line)
            inner_classes.extend(visitor.classes)

        self.get_raw_metrics(node)
        cls_metrics = RawClassMetrics(
            classname,
            node.lineno,
            node.col_offset,
            max(visitors_max_lines + list(map(GET_ENDLINE, methods))),
            methods,
            inner_classes,
            self.loc,
            self.lloc,
            self.sloc,
            self.comments,
            self.multi,
            self.blank,
            self.single_comments,
        )
        self.classes.append(cls_metrics)
