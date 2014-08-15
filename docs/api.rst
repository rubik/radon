Using radon programmatically
============================

Radon has a set of functions and classes that you can call from within your
program to analyze files.

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
