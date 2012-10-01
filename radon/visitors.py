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


class Function(BaseFunc):

    @property
    def letter(self):
        return 'M' if self.is_method else 'F'

    @property
    def fullname(self):
        if self.classname is None:
            return self.name
        return '{0}.{1}'.format(self.classname, self.name)

    def __str__(self):
        return '{0} {1}:{2} {3} - {4}'.format(self.letter, self.lineno,
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
        return int(self.real_complexity / float(len(self.methods))) + 1

    def __str__(self):
        return '{0} {1}:{2} {3} - {4}'.format(self.letter, self.lineno,
                                              self.col_offset, self.name,
                                              self.complexity)


class CodeVisitor(ast.NodeVisitor):

    @staticmethod
    def get_name(obj):
        return obj.__class__.__name__

    @classmethod
    def from_code(cls, code, **kwargs):
        return cls.from_ast(ast.parse(code), **kwargs)

    @classmethod
    def from_ast(cls, ast_node, **kwargs):
        visitor = cls(**kwargs)
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

    @property
    def blocks(self):
        blocks = self.functions
        for cls in self.classes:
            blocks.append(cls)
            blocks.extend(cls.methods)
        return blocks

    def generic_visit(self, node):
        # Get the name of the class
        name = self.get_name(node)
        # The Try/Except block is counted as the number of handlers
        # plus the `else` block.
        # In Python 3.3 the TryExcept and TryFinally nodes have been merged
        # into a single node: Try
        if name in ('Try', 'TryExcept'):
            self.complexity += len(node.handlers) + len(node.orelse)
        elif name == 'BoolOp':
            self.complexity += len(node.values) - 1
        # Lambda functions, ifs, with and assert statements count all as 1.
        elif name in ('Lambda', 'With', 'If', 'IfExp', 'Assert'):
            self.complexity += 1
        # The For and While blocks count as 1 plus the `else` block.
        elif name in ('For', 'While'):
            self.complexity += len(node.orelse) + 1
        # List, set, dict comprehensions and generator exps count as 1 plus
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
        body_complexity = 0
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
        # According to Cyclomatic Complexity definition it has to start off
        # from 1.
        body_complexity = 1
        classname = node.name
        for child in node.body:
            visitor = ComplexityVisitor(True, classname, off=False)
            visitor.visit(child)
            methods.extend(visitor.functions)
            body_complexity += visitor.complexity

        body_complexity += sum(map(GET_COMPLEXITY, methods)) - len(methods)
        cls = Class(classname, node.lineno, node.col_offset,
                    methods, body_complexity)
        self.classes.append(cls)


class HalsteadVisitor(CodeVisitor):

    types = {ast.Num: 'n',
             ast.Name: 'id',
    }

    def __init__(self, context=None):
        self.operators_seen = set()
        self.operands_seen = set()
        self.operators = 0
        self.operands = 0
        self.context = context

    @property
    def distinct_operators(self):
        return len(self.operators_seen)

    @property
    def distinct_operands(self):
        return len(self.operands_seen)

    def generic_visit(self, node):
        name = node.__class__.__name__
        operands_seen = []
        if name == 'BinOp':
            self.operators += 1
            self.operands += 2
            self.operators_seen.add(self.get_name(node.op))
            operands_seen = (node.left, node.right)
        elif name == 'UnaryOp':
            self.operators += 1
            self.operands += 1
            self.operators_seen.add(self.get_name(node.op))
            operands_seen = [node.operand]
        elif name == 'BoolOp':
            self.operators += 1
            self.operands += len(node.values)
            self.operators_seen.add(self.get_name(node.op))
            operands_seen = node.values
        elif name == 'AugAssign':
            self.operators += 1
            self.operands += 2
            self.operators_seen.add(self.get_name(node.op))
            operands_seen = (node.target, node.value)
        for operand in operands_seen:
            if operand.__class__ in self.types:
                operand = getattr(operand, self.types[operand.__class__])
            self.operands_seen.add((self.context, operand))

        super(HalsteadVisitor, self).generic_visit(node)

    def visit_FunctionDef(self, node):
        for child in node.body:
            visitor = HalsteadVisitor.from_ast(child, context=node.name)
            self.operators += visitor.operators
            self.operands += visitor.operands
            self.operators_seen.update(visitor.operators_seen)
            self.operands_seen.update(visitor.operands_seen)
