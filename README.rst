Radon
=====

.. image:: https://img.shields.io/codacy/grade/623b84f5f6e6708c486f371e10da3610.svg?style=for-the-badge
   :alt: Codacy badge
   :target: https://www.codacy.com/app/rubik/radon/dashboard

.. image:: https://img.shields.io/travis/rubik/radon/master.svg?style=for-the-badge
    :alt: Travis-CI badge
    :target: https://travis-ci.org/rubik/radon

.. image:: https://img.shields.io/coveralls/rubik/radon/master.svg?style=for-the-badge
    :alt: Coveralls badge
    :target: https://coveralls.io/r/rubik/radon?branch=master

.. image:: https://img.shields.io/pypi/v/radon.svg?style=for-the-badge
    :alt: PyPI latest version badge
    :target: https://pypi.python.org/pypi/radon

.. image:: https://img.shields.io/pypi/l/radon.svg?style=for-the-badge
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

Radon will run from **Python 2.7** to **Python 3.8** (except Python versions
from 3.0 to 3.3) with a single code base and without the need of tools like
2to3 or six. It can also run on **PyPy** without any problems (currently PyPy
3.5 v7.3.1 is used in tests).

Radon depends on as few packages as possible. Currently only `mando` is
strictly required (for the CLI interface). `colorama` is also listed as a
dependency but if Radon cannot import it, the output simply will not be
colored.

**Note**:
**Python 2.6** was supported until version 1.5.0. Starting from version 2.0, it
is not supported anymore.

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


**Note about file encoding**

On some systems, such as Windows, the default encoding is not UTF-8. If you are
using Unicode characters in your Python file and want to analyze it with Radon,
you'll have to set the `RADONFILESENCODING` environment variable to `UTF-8`.


On a Continuous Integration server
----------------------------------

If you are looking to use `radon` on a CI server you may be better off with
`xenon <https://github.com/rubik/xenon>`_. Although still experimental, it will
fail (that means exiting with a non-zero exit code) when various thresholds are
surpassed. `radon` is more of a reporting tool, while `xenon` is a monitoring
one.

If you are looking for more complete solutions, read the following sections.

Codacy
++++++++++++

`Codacy <https://www.codacy.com/>`_ uses Radon `by default <https://support.codacy.com/hc/en-us/articles/213632009-Engines#other-tools>`_ to calculate metrics from the source code.

Code Climate
++++++++++++

Radon is available as a `Code Climate Engine <https://docs.codeclimate.com/docs/list-of-engines>`_.
To understand how to add Radon's checks to your Code Climate Platform, head
over to their documentation:
https://docs.codeclimate.com/v1.0/docs/radon

coala Analyzer
++++++++++++++

Radon is also supported in `coala <http://coala.io/>`_. To add Radon's
checks to coala, simply add the ``RadonBear`` to one of the sections in
your ``.coafile``.

CodeFactor
++++++++++++

`CodeFactor <https://www.codefactor.io/>`_ uses Radon `out-of-the-box <https://support.codefactor.io/i24-analysis-tools-open-source>`_ to calculate Cyclomatic Complexity.

Usage with Jupyter Notebooks
----------------------------

Radon can be used with ``.ipynb`` files to inspect code metrics for Python cells. Any ``%`` macros will be ignored in the metrics.

.. note::

   Jupyter Notebook support requires the optional ``nbformat`` package. To install, run ``pip install nbformat``.

To enable scanning of Jupyter notebooks, add the ``--include-ipynb`` flag.

To enable reporting of individual cells, add the ``--ipynb-cells`` flag.

Quick example:

.. code-block:: sh

    $ radon raw --include-ipynb --ipynb-cells .
    example.ipynb
        LOC: 63
        LLOC: 37
        SLOC: 37
        Comments: 3
        Single comments: 2
        Multi: 10
        Blank: 14
        - Comment Stats
            (C % L): 5%
            (C % S): 8%
            (C + M % L): 21%
    example.ipynb:[0]
        LOC: 0
        LLOC: 0
        SLOC: 0
        Comments: 0
        Single comments: 0
        Multi: 0
        Blank: 0
        - Comment Stats
            (C % L): 0%
            (C % S): 0%
            (C + M % L): 0%
    example.ipynb:[1]
        LOC: 2
        LLOC: 2
        SLOC: 2
        Comments: 0
        Single comments: 0
        Multi: 0
        Blank: 0
        - Comment Stats
            (C % L): 0%
            (C % S): 0%
            (C + M % L): 0%



Links
-----

* Documentation: https://radon.readthedocs.org
* PyPI: http://pypi.python.org/pypi/radon
* Issue Tracker: https://github.com/rubik/radon/issues
