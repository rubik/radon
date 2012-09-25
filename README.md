## Radon

Quick example:

    $ radon cc -anc ../autopep8/autopep8.py 
    ../autopep8/autopep8.py
        M 1215:4 Wrapper.pep8_expected - F
        C 1145:0 Wrapper - D
        M 1023:4 Reindenter.run - C

    72 blocks (classes, functions, methods) analyzed.
    Average complexity: A (1.9)

Actually it's even better: it's got colors!

![A screen of radon](http://cloud.github.com/downloads/rubik/radon/radon_cc.png 'A screen of radon')


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

TODO
