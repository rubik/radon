Radon
#####

.. image:: https://travis-ci.org/rubik/radon.png?branch=master
    :alt: Travis-CI badge
    :target: https://travis-ci.org/rubik/radon

.. image:: https://landscape.io/github/rubik/radon/master/landscape.png
   :target: https://landscape.io/github/rubik/radon/master
   :alt: Code Health

.. image:: https://coveralls.io/repos/rubik/radon/badge.png?branch=master
    :alt: Coveralls badge
    :target: https://coveralls.io/r/rubik/radon?branch=master

.. image:: https://pypip.in/v/radon/badge.png
    :alt: PyPI latest version badge
    :target: https://crate.io/packages/radon

.. image:: https://pypip.in/d/radon/badge.png
    :alt: PyPI downloads badge
    :target: https://crate.io/packages/radon

.. image:: https://gemnasium.com/rubik/radon.png
    :alt: Dependency Status
    :target: https://gemnasium.com/rubik/radon

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
without any problems (currently only PyPy 2.0.0 is tested).

Radon depends on as few packages as possible. Currently only `mando` is
strictly required (for the CLI interface). `colorama` is also listed as a
dependency but if Radon cannot import it, the output simply will not be
colored.

Installation
------------

With Pip::

    $ pip install radon

Or download the source and run the setup file::

    $ python setup.py install

Usage
-----

Radon can be used either from the command line or programmatically.
Documentation is at https://radon.readthedocs.org/.

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
