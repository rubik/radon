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

Blocks are also classified into three types: functions, methods and classes.
They're listed by letter in the command output for convenience when scanning
through a longer list of blocks:

    ============ ========
     Block type   Letter
    ============ ========
     Function     F
     Method       M
     Class        C
    ============ ========

Options
+++++++

.. option:: -x, --max

   Set the maximum complexity rank to display.

.. option:: -n, --min

   Set the minimum complexity rank to display.

.. option:: -a, --average

   If given, at the end of the analysis show the average Cyclomatic
   Complexity. This option is influenced by :option:`-x, --max` and
   :option:`-n, --min` options.

.. option:: --total-average

   Like :option:`-a, --average`, but it is not influenced by `min` and `max`.
   Every analyzed block is counted, no matter whether it is displayed or not.

.. option:: -s, --show_complexity

   If given, show the complexity score along with its rank.

.. option:: -e, --exclude

   Exclude files only when their path matches one of these glob patterns.
   Usually needs quoting at the command line.

.. option:: -i, --ignore

   Ignore directories when their name matches one of these glob patterns: radon
   won't even descend into them. By default, hidden directories (starting with
   '.') are ignored.

.. option:: -o, --order

   The ordering function for the results. Can be one of:

    * `SCORE`: order by cyclomatic complexity (descending):
    * `LINES`: order by line numbers;
    * `ALPHA`: order by block names (alphabetically).

.. option:: -j, --json

   If given, the results will be converted into JSON. This is useful in case
   you need to export the results to another application.

.. option:: --xml

   If given, the results will be converted into XML. Note that not all the
   information is kept. This is specifically targeted to Jenkin's plugin CCM.

.. option:: --no-assert

   Does not count assert statements when computing complexity. This is because
   Python can be run with an optimize flag which removes assert statements.

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

   Remember to quote the patterns, otherwise your shell might expand them!

Depending on the single cases, a more suitable alternative might be this::

    $ radon cc -i "docs,tests" path

::

    $ cat path/to/file.py | radon cc -

Setting the path to "-" will cause Radon to analyze code from stdin

::

    $ radon cc --min B --max E path

Here Radon will only display blocks ranked between B and E (i.e. from ``CC=6``
to ``CC=40``).


The :command:`mi` command
-------------------------

.. program:: mi

This command analyzes Python source code files and compute the Maintainability
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

.. option:: -x, --max

   Set the maximum MI to display.

.. option:: -n, --min

   Set the minimum MI to display.

.. option:: -e, --exclude

   Exclude files only when their path matches one of these glob patterns.
   Usually needs quoting at the command line.

.. option:: -i, --ignore

   Ignore directories when their name matches one of these glob patterns: radon
   won't even descend into them. By default, hidden directories (starting with
   '.') are ignored.

.. option:: -m, --multi

   If given, Radon will not count multiline strings as comments.
   Most of the time this is safe since multiline strings are used as functions
   docstrings, but one should be aware that their use is not limited to that
   and sometimes it would be wrong to count them as comment lines.

.. option:: -s, --show

   If given, the actual MI value is shown in results, alongside the rank.

.. option:: -j, --json

   Format results in JSON.


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

.. program:: raw

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

   Exclude files only when their path matches one of these glob patterns.
   Usually needs quoting at the command line.

.. option:: -i, --ignore

   Ignore directories when their name matches one of these glob patterns: radon
   won't even descend into them. By default, hidden directories (starting with
   '.') are ignored.

.. option:: -s, --summary

   If given, at the end of the analysis a summary of the gathered
   metrics will be shown.

.. option:: -j, --json

   If given, the results will be converted into JSON.

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
