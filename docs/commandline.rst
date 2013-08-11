Command-line Usage
==================

Radon currently has three commands:

    * :command:`cc`: compute Cyclomatic Complexity
    * :command:`raw`: compute raw metrics
    * :command:`mi`: compute Maintainability Index

The :command:`cc` command
-------------------------

.. program:: cc

This command analyzes Python source files and compute Cyclomatic Complexity.
The output can be filtered by specifying the :option:`-n` and :option:`-x`
flags. By default, the complexity score is not displayed, the option
:option:`-s` (show complexity) toggles this behaviour. File or directories
exclusion is supported through glob patterns. Every positional argument is
interpreted as a path. The program then walks through its children and analyzes
Python files.
Every block will be ranked from A (best complexity score) to F (worst one).
Ranks corresponds to complexity scores as follows:

    ========== ====== =========================================
     CC score   Rank   Risk
    ========== ====== =========================================
     1 - 5      A      low - simple block
     6 - 10     B      low - well structured and stable block
     11 - 20    C      moderate - slightly complex block
     21 - 30    D      more than moderate - more complex block
     31 - 40    E      high - complex block, alarming
       41+      F      very high - error-prone, unstable block
    ========== ====== =========================================

Options
+++++++

.. option:: -x, --max

    Set the maximum complexity rank to display.

.. option:: -n, --min

    Set the minimum complexity rank to display.

.. option:: -a, --average

    If given, at the end of the analysis show the average Cyclomatic
    Complexity.

.. option:: -s, --show_complexity

    If given, show the complexity score along with its rank.

.. option:: -e, --exclude

    A comma-separated list of patterns which indicate which paths to exclude
    from the analysis.

Examples
++++++++

::

    $ radon cc path

Radon will walk through the subdirectories of path and will analyze all
child nodes (every Python file it encounters).

::

    $ radon cc -e "path/tests*,path/docs/*" path

As in the above example, Radon will walk the directories, excluding paths
matching ``path/tests/*`` and ``path/docs/*``.

.. warning::
    Remember to quote the patterns, otherwise your shell will expand them!


::

    $ radon cc --min B --max E path

Here Radon will only display blocks ranked between B and E (i.e. from ``CC=6``
to ``CC=40``).


The :command:`mi` command
-------------------------

.. program:: mi

The command analyzes Python source code files and compute the Maintainability
Index score.
Every positional argument is treated as a starting point from which to walk
looking for Python files (as in the :command:`cc` command). Paths can be
excluded with the :option:`-e` option.
The Maintainability Index is always in the range 0-100. MI is ranked as
follows:

    ========== ====== =================
     MI score   Rank   Maintainability
    ========== ====== =================
     100 - 20    A     Very high
      19 - 10    B     Medium
       9 - 0     C     Extremely low
    ========== ====== =================


Options
+++++++

.. option:: -e, --exclude

    A comma-separated list of patterns which indicate which paths to exclude
    from the analysis.

.. option:: -m, --multi

    Whether or not to count multiline strings as comments (default to yes).
    Most of the time this is safe since multiline strings are used as
    functions docstrings, but one should be aware that their use is not
    limited to that and sometimes it would be wrong to count them as comment lines.


Examples
++++++++

::

    $ radon mi path1 path2

Analyze every Python file under *path1* or *path2*. It checks recursively in
every subdirectory.


::

    $ radon mi path1 -e "path1/tests/*"

Like the previous example, but excluding from the analysis every path that
matches `path1/tests/*`.

::

    $ radon mi -m path1

Like the previous examples, but does not count multiline strings as comments.


The :command:`raw` command
--------------------------

This command analyzes the given Python modules in order to compute raw metrics.
These include:

    * **LOC**: the total number of lines of code
    * **LLOC**: the number of logical lines of code
    * **SLOC**: the number of source lines of code - not necessarily
      corresponding to the **LLOC** [Wikipedia]_
    * **comments**: the number of Python comment lines (i.e. only single-line
      comments ``#``)
    * **multi**: the number of lines representing multi-line strings
    * **blank**: the number of blank lines (or whitespace-only ones)

The equation :math:`sloc + blank = loc` should always hold.

.. [Wikipedia] More information on **LOC**, **SLOC**, **LLOC** here: http://en.wikipedia.org/wiki/Source_lines_of_code


Options
+++++++

.. option:: -e, --exclude

    A comma-separated list of patterns which indicate which paths to exclude
    from the analysis.

Examples
++++++++

::

    $ radon raw path1 path2

Analyze every Python file under *path1* or *path2*. It checks recursively in
every subdirectory.

::

    $ radon raw path1 -e "path1/tests/*"

Like the previous example, but excluding from the analysis every path that
matches ``path1/tests/*``.
