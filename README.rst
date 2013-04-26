Radon
#####

Radon is a tool for Python that computes various metrics from the source code.
Radon can compute

* **McCabe's complexity**, i.e. cyclomatic complexity
* **raw** metrics (these include SLOC, comment lines, blank lines, &c.)
* **Halstead** metrics (all of them)
* **Maintainability Index** (the one used in Visual Studio)

Requirements
------------

Radon will run from **Python 2.6** to **Python 3.3** (endpoints inclusive) with a
single code base and without the need of tools like 2to3 or six. It can also
run on **PyPy** without any problems (version tested: 1.9 and 2.0.0).

Radon does not depend on any other Python package.

Installation
------------

With Pip::

    $ pip install radon

Or download the source and run the setup file::

    $ python setup.py install

Usage
-----

Radon can be used either from the command line or programmatically.
Documentation is WIP at https://radon.readthedocs.org/.

Cyclomatic Complexity Example
-----------------------------

Quick example::

    $ radon cc -anc ../baker/baker.py
    ../baker/baker.py
        M 581:4 Baker.parse_args - D
        M 723:4 Baker.parse - D
        M 223:4 Baker.command - C
        M 796:4 Baker.apply - C
        M 857:4 Baker.run - C

    32 blocks (classes, functions, methods) analyzed.
    Average complexity: B (6.15625)

Explanation:

* ``cc`` is the radon command
* ``-a`` tells radon to calculate the average complexity at the end
* ``-nc`` tells radon to print only results with a complexity rank of C or
  worse. Other examples: ``-na`` (from A to F), or ``-nd`` (from D to F).

Actually it's even better: it's got colors!

.. image:: http://cloud.github.com/downloads/rubik/radon/radon_cc.png
    :alt: A screen of Radon's cc command

Links
-----

* Documentation: https://radon.readthedocs.org
* PyPI: http://pypi.python.org/pypi/radon
