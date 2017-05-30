Introduction to Code Metrics
============================

This section contains a brief explanations of the metrics that Radon can
compute.


Cyclomatic Complexity
---------------------

Cyclomatic Complexity corresponds to the number of decisions a block of code
contains plus 1. This number (also called McCabe number) is equal to the number
of linearly independent paths through the code. This number can be used as a
guide when testing conditional logic in blocks.

Radon analyzes the AST tree of a Python program to compute Cyclomatic
Complexity. Statements have the following effects on Cyclomatic Complexity:

================== ============== ===========================================================================================
 Construct          Effect on CC   Reasoning
================== ============== ===========================================================================================
 if                 +1             An `if` statement is a single decision.
 elif               +1             The `elif` statement adds another decision.
 else               +0             The `else` statement does not cause a new decision. The decision is at the `if`.
 for                +1             There is a decision at the start of the loop.
 while              +1             There is a decision at the `while` statement.
 except             +1             Each `except` branch adds a new conditional path of execution.
 finally            +0             The finally block is unconditionally executed.
 with               +1             The `with` statement roughly corresponds to a try/except block (see PEP 343 for details).
 assert             +1             The `assert` statement internally roughly equals a conditional statement.
 Comprehension      +1             A list/set/dict comprehension of generator expression is equivalent to a for loop.
 Boolean Operator   +1             Every boolean operator (and, or) adds a decision point.
================== ============== ===========================================================================================


Maintainability Index
---------------------
Maintainability Index is a software metric which measures how maintainable
(easy to support and change) the source code is. The maintainability index is
calculated as a factored formula consisting of SLOC (Source Lines Of Code),
Cyclomatic Complexity and Halstead volume. It is used in several automated
software metric tools, including the Microsoft Visual Studio 2010 development
environment, which uses a shifted scale (0 to 100) derivative.

Common formulas are:

* the original formula:

  .. math::

    MI = 171 - 5.2 \ln V - 0.23 G - 16.2 \ln L

* the derivative used by SEI:

  .. math::

    MI = 171 - 5.2\log_2 V - 0.23 G - 16.2 \log_2 L + 50 \sin(\sqrt{2.4 C})

* the derivative used by Visual Studio:

  .. math::

    MI = \max \left [ 0, 100\dfrac{171 - 5.2\ln V - 0.23 G - 16.2 \ln L}{171} \right ].

Radon uses another derivative, computed from both SEI derivative and Visual
Studio one:

.. math::

    MI = \max \left [ 0, 100\dfrac{171 - 5.2\ln V - 0.23 G - 16.2 \ln L + 50 \sin(\sqrt{2.4 C}))}{171} \right ]

Where:
    * ``V`` is the Halstead Volume (see below);
    * ``G`` is the total Cyclomatic Complexity;
    * ``L`` is the number of Source Lines of Code (SLOC);
    * ``C`` is the percent of comment lines (important: converted to radians).

.. note:: Maintainability Index is still a very experimental metric, and
   should not be taken into account as seriously as the other metrics.

Raw Metrics
-----------

The following are the definitions employed by Radon:

    * **LOC**: The total number of lines of code. It does not necessarily
      correspond to the number of lines in the file.
    * **LLOC**: The number of logical lines of code. Every logical line of code
      contains exactly one statement.
    * **SLOC**: The number of source lines of code - not necessarily
      corresponding to the **LLOC**.
    * Comments: The number of comment lines. Multi-line strings are not counted
      as comment since, to the Python interpreter, they are just strings.
    * Multi: The number of lines which represent multi-line strings.
    * Blanks: The number of blank lines (or whitespace-only ones).

The equation ``SLOC + Multi + Single comments + Blank = LOC`` should always
hold.  Additionally, comment stats are calculated:

    * `C % L`: the ratio between number of comment lines and **LOC**,
      expressed as a percentage;
    * `C % S`: the ratio between number of comment lines and **SLOC**,
      expressed as a percentage;
    * `C + M % L`: the ratio between number of comment and multiline strings
      lines and **LOC**, expressed as a percentage.

Halstead Metrics
----------------

Halstead's goal was to identify measurable properties of software, and the
relations between them. These numbers are statically computed from the source
code:

    * :math:`\eta_1` = the number of distinct operators
    * :math:`\eta_2` = the number of distinct operands
    * :math:`N_1` = the total number of operators
    * :math:`N_2` = the total number of operands

From these numbers several measures can be calculated:

    * Program vocabulary: :math:`\eta = \eta_1 + \eta_2`
    * Program length: :math:`N = N_1 + N_2`
    * Calculated program length: :math:`\widehat{N} = \eta_1 \log_2 \eta_1 +
      \eta_2 \log_2 \eta_2`
    * Volume: :math:`V = N \log_2 \eta`
    * Difficulty: :math:`D = \dfrac{\eta_1}{2} \cdot \dfrac{N_2}{\eta_2}`
    * Effort: :math:`E = D \cdot V`
    * Time required to program: :math:`T = \dfrac{E}{18}` seconds
    * Number of delivered bugs: :math:`B = \dfrac{V}{3000}`.

Further Reading
---------------

1. Paul Omand and Jack Hagemeister. “Metrics for assessing a software system’s
   maintainability”. Proceedings International Conference on Software
   Mainatenance (ICSM), 1992. (`doi <http://dx.doi.org/10.1109/ICSM.1992.242525>`_)

2. Don M. Coleman, Dan Ash, Bruce Lowther, Paul W. Oman. Using Metrics to
   Evaluate Software System Maintainability. IEEE Computer 27(8), 1994. (`doi
   <http://doi.ieeecomputersociety.org/10.1109/2.303623>`_, `postprint
   <http://www.ecs.csun.edu/~rlingard/comp589/ColemanPaper.pdf>`_)

3. `Maintainability Index Range and Meaning
   <http://blogs.msdn.com/b/codeanalysis/archive/2007/11/20/maintainability-index-range-and-meaning.aspx>`_.
   Code Analysis Team Blog, blogs.msdn, 20 November 2007.

4. Arie van Deursen, `Think Twice Before Using the “Maintainability Index”
   <http://avandeursen.com/2014/08/29/think-twice-before-using-the-maintainability-index/>`_.
