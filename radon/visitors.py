import ast
import operator
import collections


# Helper functions to use in combination with map()
GET_COMPLEXITY = operator.attrgetter('complexity')
NAMES_GETTER = operator.attrgetter('name', 'asname')

BaseFunc = collections.namedtuple('Function', ['name', 'lineno', 'col_offset',
                                               'is_method', 'classname',
                                               'complexity'])
BaseClass = collections.namedtuple('Class', ['name', 'lineno', 'col_offset',
                                             'methods', 'real_complexity'])

Import = collections.namedtuple('Import', 'name asname')
ImportFrom = collections.namedtuple('ImportFrom', 'module name asname')


class Function(BaseFunc):

    @property
    def letter(self):
        return 'M' if self.is_method else 'F'

    @property
    def fullname(self):
        if self.classname is None:
            return self.name
        return '{}.{}'.format(self.classname, self.name)

    def __str__(self):
        return '{} {}:{} {} - {}'.format(self.letter, self.lineno,
                                         self.col_offset, self.fullname,
                                         self.complexity)


class Class(BaseClass):

    letter = 'C'

    @property
    def fullname(self):
        return self.name

    @property
    def complexity(self):
        if not self.methods:
            return self.real_complexity
        return self.real_complexity / len(self.methods)

    def __str__(self):
        return '{} {}:{} {} - {}'.format(self.letter, self.lineno,
                                         self.col_offset, self.name,
                                         self.complexity)


class CodeVisitor(ast.NodeVisitor):

    @classmethod
    def from_code(cls, code):
        return cls.from_ast(ast.parse(code))

    @classmethod
    def from_ast(cls, ast_node):
        visitor = cls()
        visitor.visit(ast_node)
        return visitor


class ComplexityVisitor(CodeVisitor):
    '''A visitor that keeps track of the cyclomatic complexity of
    the elements.
    '''

    def __init__(self, to_method=False, classname=None, off=True):
        self.complexity = 1 if off else 0
        self.functions = []
        self.classes = []
        self.to_method = to_method
        self.classname = classname

    def __repr__(self):
        return 'ComplexityVisitor(complexity={})'.format(self.complexity)

    @property
    def functions_complexity(self):
        return sum(map(GET_COMPLEXITY, self.functions))

    @property
    def classes_complexity(self):
        return sum(map(GET_COMPLEXITY, self.classes))

    @property
    def total_complexity(self):
        return (self.complexity + self.functions_complexity +
                self.classes_complexity)

    def generic_visit(self, node):
        # Get the name of the class
        name = node.__class__.__name__
        # The Try/Except block is counted as the number of handlers
        # plus the `else` block.
        if name == 'TryExcept':
            self.complexity += len(node.handlers) + len(node.orelse)
        elif name == 'BoolOp':
            self.complexity += len(node.values) - 1
        # Lambda functions and with statement count as 1.
        elif name in ('Lambda', 'With'):
            self.complexity += 1
        # The If, For and While blocks count as 1 plus the `else` block.
        elif name in ('If', 'For', 'While'):
            self.complexity += len(node.orelse) + 1
        # List comprehensions and generator exps count as 1 plus
        # the `if` statement.
        elif name == 'comprehension':
            self.complexity += len(node.ifs) + 1

        super(ComplexityVisitor, self).generic_visit(node)

    def visit_FunctionDef(self, node):
        # The complexity of a function is computed taking into account
        # the following factors: number of decorators, the complexity
        # the function's body and the number of clojures (which count
        # double).
        clojures = []
        body_complexity = len(node.decorator_list)
        for child in node.body:
            visitor = ComplexityVisitor(off=False)
            visitor.visit(child)
            clojures.extend(visitor.functions)
            # Add general complexity and clojures' complexity
            body_complexity += (visitor.complexity +
                                visitor.functions_complexity)

        # Follow Cyclomatic Complexity definition
        body_complexity += 1
        func = Function(node.name, node.lineno, node.col_offset,
                        self.to_method, self.classname, body_complexity)
        self.functions.append(func)


    def visit_ClassDef(self, node):
        # The complexity of a class is computed taking into account
        # the following factors: number of decorators and the complexity
        # of the class' body (which is the sum of all the complexities).
        methods = []
        body_complexity = len(node.decorator_list)
        classname = node.name
        for child in node.body:
            visitor = ComplexityVisitor(True, classname, off=False)
            visitor.visit(child)
            methods.extend(visitor.functions)
            body_complexity += (visitor.complexity +
                                visitor.functions_complexity)

        # According to Cyclomatic Complexity definition it has to start off
        # from 1.
        body_complexity += 1
        cls = Class(classname, node.lineno, node.col_offset,
                    methods, body_complexity)
        self.classes.append(cls)



class ImportsVisitor(CodeVisitor):

    def __init__(self):
        self.imports = []
        self.imports_from = []

    def visit_Import(self, node):
        imps = map(NAMES_GETTER, node.names)
        self.imports.extend(Import(*args) for args in imps)

    def visit_ImportFrom(self, node):
        imps = (ImportFrom(node.module, *map(NAMES_GETTER, name))
                for name in node.names)
        self.imports_from.extend(imps)
