pyecoregen - Python code generation from pyecore models
=======================================================

|pypi-version| |master-build| |coverage| |license|

.. |master-build| image:: https://travis-ci.org/pyecore/pyecoregen.svg?branch=master
    :target: https://travis-ci.org/pyecore/pyecoregen

.. |pypi-version| image:: https://badge.fury.io/py/pyecoregen.svg
    :target: https://badge.fury.io/py/pyecoregen

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

The library works with any version of Python >= 3.3.

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

Programmatic interface
~~~~~~~~~~~~~~~~~~~~~~

If you need to generate code from an in-memory representation of a pyecore model, you instantiate
the ``EcoreGenerator`` class and call the generate method. Assuming you have loaded above model and
hold it's root package in ``library_pkg``, you would generate with:

.. code-block:: python

    generator = EcoreGenerator()
    generator.generate(library_pkg, 'some/folder')
