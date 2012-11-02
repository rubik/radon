Radon
#####

Radon is a tool for Python that computes various metrics from the source code.
Radon does not only compute McCabe's complexity, but also:

* raw metrics (these include SLOC, comment lines, blank lines, &c.)
* Halstead metrics (all of them)
* Maintainability Index (the one used in Visual Studio)

Usage
-----

Radon can be used either from the command line or programmatically.
Documentation is WIP at https://radon.readthedocs.org/.

Cyclomatic Complexity
---------------------

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

Actually it's even better: it's got colors!

.. image:: http://cloud.github.com/downloads/rubik/radon/radon_cc.png
    :alt: A screen of Radon's cc command


Command's help::

    $ radon cc -h
    Usage: /home/miki/exp/bin/radon cc [<min>] [<max>] [<show_complexity>] [<average>] [<paths>...]

    Analyze the given Python modules and compute Cyclomatic Complexity (CC).

        The output can be filtered using the *min* and *max* flags. In addition
        to y default, complexity score is not displayed.

    Options:

       -x --max              The maximum complexity to display (default to F).
       -a --average          If True, at the end of the analysis display the
                               average complexity. Default to False.
       -s --show_complexity  Whether or not to show the actual complexity score
                               together with the A-F rank. Default to False.
       -n --min              The minimum complexity to display (default to A).

    Variable arguments:

       *paths The modules or packages to analyze.
