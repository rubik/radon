Using radon programmatically
============================

Radon has a set of functions and classes that you can call from within your
program to analyze files.

Radon's API is composed of three layers:

* at the very bottom (the lowest level) there are the **Visitors**: with these
  classes one can build an AST out of the code and get basic metrics.
  Currently, there are two available visitors:
  :class:`~radon.visitors.ComplexityVisitor` and
  :class:`~radon.visitors.HalsteadVisitor`. With the former one analyzes the
  cyclomatic complexity of the code, while the latter gathers the so-called
  Halstead metrics. With those and other raw metrics one can compute the
  Maintainability Index. Example:

  .. code-block:: python

      >>> from radon.visitors import ComplexityVisitor
      >>> v = ComplexityVisitor.from_code('''
      def factorial(n):
          if n < 2: return 1
          return n * factorial(n - 1)

      def foo(bar):
          return sum(i for i in range(bar ** 2) if bar % i)
      ''')
      >>> v.functions
      [Function(name='factorial', lineno=2, col_offset=0, endline=4, is_method=False,
      classname=None, closures=[], complexity=2),
      Function(name='foo', lineno=6, col_offset=0, endline=7, is_method=False, classname=None,
      closures=[], complexity=3)]

* at a higher level, there are helper functions residing in separate modules.
  For cyclomatic complexity, one can use those inside :mod:`radon.complexity`.
  For Halstead metrics and MI index those inside :mod:`radon.metrics`. Finally,
  for raw metrics (that includes SLOC, LLOC, LOC, &c.) one can use the function
  :func:`~radon.raw.analyze` inside the :mod:`radon.raw` module. With the
  majority of these functions the result is an object (``Module`` object in the
  case of raw metrics) or a list of objects (``Function`` or ``Class`` objects
  for cyclomatic complexity). Example:

  .. code-block:: python

      >>> from radon.complexity import cc_rank, cc_visit
      >>> cc_rank(4), cc_rank(9), cc_rank(14), cc_rank(23)
      ('A', 'B', 'C', 'D')
      >>> cc_visit('''
      class A(object):
          def meth(self):
              return sum(i for i in range(10) if i - 2 < 5)

      def fib(n):
          if n < 2: return 1
          return fib(n - 1) + fib(n - 2)
      ''')

      [Function(name='fib', lineno=6, col_offset=0, endline=8, is_method=False, classname=None,
      closures=[], complexity=2), Class(name='A', lineno=2, col_offset=0, endline=4,
      methods=[Function(name='meth', lineno=3, col_offset=4, endline=4, is_method=True,
      classname='A', closures=[], complexity=3)], real_complexity=3),
      Function(name='meth', lineno=3, col_offset=4, endline=4, is_method=True, classname='A',
      closures=[], complexity=3)]

      >>> from radon.raw import analyze
      >>> analyze("""def _split_tokens(tokens, token, value):
          '''Split a list of tokens on the specified token pair (token, value),
          where *token* is the token type (i.e. its code) and *value* its actual
          value in the code.
          '''
          res = [[]]
          for token_values in tokens:
              if (token, value) == token_values[:2]:
                  res.append([])
                  continue
              res[-1].append(token_values)
          return res
      """)
      >>> Module(loc=12, lloc=9, sloc=12, comments=0, multi=4, blank=0)

* at the highest level there are the **Harvesters**. A Harvester implements all
  the business logic of the CLI interface. To use a Harvester, it's sufficient
  to create a :class:`~radon.cli.Config` object (which contains all the config
  values) and pass it to the Harvester instance along with a list of paths to
  analyze. An Harvester can then export its result to various formats (for
  cyclomatic complexity both JSON and XML are available). It's possible to find
  an example for this in the `Xenon project
  <https://github.com/rubik/xenon/blob/master/xenon/core.py>`_.


Cyclomatic Complexity
---------------------

.. py:module:: radon.complexity
    :synopsis: Complexity-related helper functions.

.. autofunction:: cc_visit

.. autofunction:: cc_visit_ast

.. autofunction:: cc_rank

.. autofunction:: sorted_results(blocks, order=SCORE)

Raw metrics
-----------

.. py:module:: radon.raw
    :synopsis: Raw metrics functions.

.. autofunction:: analyze

Other metrics
-------------

.. py:module:: radon.metrics
    :synopsis: Halstead and Maintainability Index functions.

.. autofunction:: h_visit

.. autofunction:: h_visit_ast

.. autofunction:: mi_visit

.. autofunction:: mi_rank

.. autofunction:: mi_parameters

.. autofunction:: mi_compute


Visitors
--------

.. py:module:: radon.visitors
    :synopsis: AST visitors (they compute cyclomatic complexity and Halstead metrics)

.. autoclass:: ComplexityVisitor

.. autoclass:: HalsteadVisitor


Harvesters
----------

.. py:module:: radon.cli.harvest
   :synopsis: Direct interface to Radon's CLI capabilities

.. autoclass:: Harvester
   :members:

   .. automethod:: __init__

.. autoclass:: CCHarvester

.. autoclass:: RawHarvester

.. autoclass:: MIHarvester
