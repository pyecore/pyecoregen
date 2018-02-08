#!/usr/bin/env python
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

if sys.version_info < (3, 3):
    sys.exit('Sorry, Python < 3.3 is not supported')


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        args = self.pytest_args if isinstance(self.pytest_args, list) else [self.pytest_args]
        errno = pytest.main(args)
        sys.exit(errno)


setup(
    name="pyecoregen",
    version='0.4.3',
    description="Model to text framework for PyEcore, including the Ecore to Python generator",
    long_description=open('README.rst').read(),
    keywords="model metamodel EMF Ecore code generator",
    url="https://github.com/pyecore/pyecoregen",
    author="Mike Pagel",
    author_email="mike@mpagel.de",

    packages=find_packages(exclude=['tests']),
    package_data={'': ['README.rst', 'LICENSE'],
                  'pyecoregen': ['templates/*']},
    include_package_data=True,
    install_requires=['pyecore', 'pymultigen', 'jinja2', 'autopep8'],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    entry_points={'console_scripts': ['pyecoregen = pyecoregen.cli:main']},

    license='BSD 3-Clause',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: BSD License",
    ]
)
