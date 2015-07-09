.. Radon documentation master file, created by
   sphinx-quickstart on Thu Oct 11 16:08:21 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Radon's documentation!
=================================

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

Radon is a Python tool which computes various code metrics. Supported metrics are:

    * raw metrics: SLOC, comment lines, blank lines, &c.
    * Cyclomatic Complexity (i.e. McCabe's Complexity)
    * Halstead metrics (all of them)
    * the Maintainability Index (a Visual Studio metric)

Radon can be used either from the command line or programmatically through its
API.

Contents:

.. toctree::
   :maxdepth: 2

   intro
   commandline
   flake8
   api
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

