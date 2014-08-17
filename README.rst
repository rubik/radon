Radon
=====

.. image:: http://img.shields.io/travis/rubik/radon/master.svg?style=flat
    :alt: Travis-CI badge
    :target: https://travis-ci.org/rubik/radon

.. image:: http://img.shields.io/coveralls/rubik/radon/master.svg?style=flat
    :alt: Coveralls badge
    :target: https://coveralls.io/r/rubik/radon?branch=master

.. image:: https://pypip.in/v/radon/badge.png?style=flat
    :alt: PyPI latest version badge
    :target: https://pypi.python.org/pypi/radon

.. image:: https://pypip.in/d/radon/badge.png?style=flat
    :alt: PyPI downloads badge
    :target: https://pypi.python.org/pypi/radon

.. image:: https://pypip.in/format/radon/badge.svg?style=flat
    :target: http://pythonwheels.com/
    :alt: Download format

.. image:: https://pypip.in/license/radon/badge.png?style=flat
    :alt: Radon license
    :target: https://pypi.python.org/pypi/radon


----

Radon is a Python tool that computes various metrics from the source code.
Radon can compute:

* **McCabe's complexity**, i.e. cyclomatic complexity
* **raw** metrics (these include SLOC, comment lines, blank lines, &c.)
* **Halstead** metrics (all of them)
* **Maintainability Index** (the one used in Visual Studio)

Requirements
------------

Radon will run from **Python 2.6** to **Python 3.4** with a single code base
and without the need of tools like 2to3 or six. It can also run on **PyPy**
without any problems (currently PyPy 2.4.0 is used in tests).

Radon depends on as few packages as possible. Currently only `mando` is
strictly required (for the CLI interface). `colorama` is also listed as a
dependency but if Radon cannot import it, the output simply will not be
colored.

Installation
------------

With Pip:

.. code-block:: sh

    $ pip install radon

Or download the source and run the setup file:

.. code-block:: sh

    $ python setup.py install

Usage
-----

Radon can be used either from the command line or programmatically.
Documentation is at https://radon.readthedocs.org/.

Cyclomatic Complexity Example
-----------------------------

Quick example:

.. code-block:: sh

    $ radon cc sympy/solvers/solvers.py -a -nc
    sympy/solvers/solvers.py
        F 346:0 solve - F
        F 1093:0 _solve - F
        F 1434:0 _solve_system - F
        F 2647:0 unrad - F
        F 110:0 checksol - F
        F 2238:0 _tsolve - F
        F 2482:0 _invert - F
        F 1862:0 solve_linear_system - E
        F 1781:0 minsolve_linear_system - D
        F 1636:0 solve_linear - D
        F 2382:0 nsolve - C

    11 blocks (classes, functions, methods) analyzed.
    Average complexity: F (61.0)

Explanation:

* ``cc`` is the radon command to compute Cyclomatic Complexity
* ``-a`` tells radon to calculate the average complexity at the end. Note that
  the average is computed among the *shown* blocks. If you want the total
  average, among all the blocks, regardless of what is being shown, you should
  use ``--total-average``.
* ``-nc`` tells radon to print only results with a complexity rank of C or
  worse. Other examples: ``-na`` (from A to F), or ``-nd`` (from D to F).
* The letter *in front of* the line numbers represents the type of the block
  (**F** means function, **M** method and **C** class).

Actually it's even better: it's got colors!

.. image:: https://cloud.githubusercontent.com/assets/238549/3707477/5793aeaa-1435-11e4-98fb-00e0bd8137f5.png
    :alt: A screen of Radon's cc command


On a Continuous Integration server
----------------------------------

If you are looking to use `radon` on a CI server you may be better off with
`xenon <https://github.com/rubik/xenon>`_. Although still experimental, it will
fail (that means exiting with a non-zero exit code) when various thresholds are
surpassed. `radon` is more of a reporting tool, while `xenon` is a monitoring
one.

Links
-----

* Documentation: https://radon.readthedocs.org
* PyPI: http://pypi.python.org/pypi/radon
* Issue Tracker: https://github.com/rubik/radon/issues
