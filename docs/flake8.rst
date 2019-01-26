Flake8 plugin
=============

.. program:: flake8

Radon exposes a plugin for the Flake8 tool. In order to use it you will have to
install both `radon` and `flake8`.

To enable the Radon checker, you will have to supply *at least* one of the
following options:

.. option:: --radon-max-cc <int>

   Set the cyclomatic complexity threshold. The default value is `10`. Blocks
   with a greater complexity will be reported by the tool.

.. option:: --radon-no-assert

   Instruct radon not to count `assert` statements towards cyclomatic
   complexity. The default behaviour is the opposite.

.. option:: --radon-show-closures

   Instruct radon to add closures/inner classes to the output.

For more information visit the `Flake8 documentation
<http://flake8.readthedocs.org/en/latest/>`_.
