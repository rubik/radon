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

Ignoring blocks
---------------

You can exclude specific functions, methods, or classes from the complexity
check by adding a ``# radon: ignore`` comment on the definition line or on
the line immediately before it:

.. code-block:: python

    def complex_function(x):  # radon: ignore
        # This function will not trigger R701
        if x > 0:
            if x > 10:
                if x > 100:
                    return x * 3
                return x * 2
        return x

This works in addition to the standard ``# noqa`` comment that Flake8 supports.

For more information visit the `Flake8 documentation
<http://flake8.readthedocs.org/en/latest/>`_.
