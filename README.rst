pyecoregen - Python code generation from pyecore models
=======================================================

|pypiversion| |masterbuild| |coverage| |license|

.. |pypiversion| image:: https://badge.fury.io/py/pyecoregen.svg
    :target: https://badge.fury.io/py/pyecoregen

.. |masterbuild| image:: https://travis-ci.org/pyecore/pyecoregen.svg?branch=master
    :target: https://travis-ci.org/pyecore/pyecoregen

.. |coverage| image:: https://coveralls.io/repos/github/pyecore/pyecoregen/badge.svg?branch=master
    :target: https://coveralls.io/github/pyecore/pyecoregen?branch=master

.. |license| image:: https://img.shields.io/badge/license-New%20BSD-blue.svg
    :target: https://raw.githubusercontent.com/pyecore/pyecoregen/develop/LICENSE

.. contents:: :depth: 2

Overview
--------

pyecoregen is a code generator, producing Python classes from Ecore models. It can be used at the
command line as well as a module. In the latter case the passed model is expected to be an instance
of the `pyecore <https://github.com/pyecore/pyecore>`_ metamodel.

After using pyecoregen, you have a Python package representing the classes from the Ecore model. The
generated classes are instances of the pyecore metaclasses. Please see `pyecore
<https://github.com/pyecore/pyecore>`_ for documentation how to work with them.

Installation
------------

pyecoregen comes in form or a regular Python distribution and can be installed from Github or PyPI
with a simple:

.. code-block:: shell

    $ pip install pyecoregen

The library works with any version of Python >= 3.4.

Usage
-----

Code generation can be done programmatically and directly at the command line.

Command line interface
~~~~~~~~~~~~~~~~~~~~~~

After installation an executable script ``pyecoregen`` has been installed. Assuming
``library.ecore`` is your Ecore XMI file, and you want to generate the classes in ``some/folder``,
you can do:

.. code-block:: bash

    $ pyecoregen -vv -e library.ecore -o some/folder

The ``-vv`` is optional to raise verbosity to log level ``DEBUG``. You should see output like this:

.. code-block::

    2017-05-26 08:06:54,303 INFO [multigen.generator] Generating code to '/here/some/folder'.
    2017-05-26 08:06:54,304 DEBUG [multigen.generator] <pyecore.ecore.EPackage object at 0x000001DCF3C61E80> --> '/here/some/folder/library/__init__.py'
    2017-05-26 08:06:54,363 DEBUG [multigen.generator] <pyecore.ecore.EPackage object at 0x000001DCF3C61E80> --> '/here/some/folder/library/library.py'


The ``pyecoregen`` command line interface also allows you to generate the classes from a
remote Ecore XMI file if its "path" starts with ``http(s)://``. The usage does not change:

.. code-block:: bash

    $ pyecoregen -e "http://path/towards/my/ecore" -o some/folder

Programmatic interface
~~~~~~~~~~~~~~~~~~~~~~

If you need to generate code from an in-memory representation of a pyecore model, you instantiate
the ``EcoreGenerator`` class and call the generate method. Assuming you have loaded above model and
hold it's root package in ``library_pkg``, you would generate with:

.. code-block:: python

    generator = EcoreGenerator()
    generator.generate(library_pkg, 'some/folder')

Generator options
~~~~~~~~~~~~~~~~~

The end user can control some of the features how the metamodel code is generated. This can be done
at the command line as well as via programmatic invocation. A command line parameter ``--my-param``
is then turning into a keyword argument ``my_param``.

``--auto-register-package`` (Default: ``False``)
    If enabled, the generated packages are automatically added to pyecore's global namespace
    registry, which makes them available during XMI deserialization.

``--user-module`` (Default: ``None``)
    If specified, the given string is interpreted as a dotted Python module path. E.g.
    ``--user-module my.custom_mod`` will make the generated code import mixin classes from a module
    ``my.custom_mod``. A generated class with name ``<name>`` then derives from a mixin
    ``<name>Mixin``, which is expected to be part of the user module. If this option is used, the
    generator also produces a skeleton file which contains all required mixin classes and methods.
    Usually you copy parts of this template to your own module, which is then checked into version
    control all your other code.

``--with-dependencies`` (Default: ``False``)
    If enabled, the generator also generates code from all metamodels that are *dependencies* of the
    input metamodel. A metamodel dependency is typically a reference from the input
    metamodel to another ``.ecore`` file. Please note that this option introduces slower code
    generation as all metamodels must be scanned in order to determine dependencies.
