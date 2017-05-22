#!/usr/bin/env python
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

if sys.version_info < (3, 3):
    sys.exit('Sorry, Python < 3.3 is not supported')


class PyTest(TestCommand):
    def run_tests(self):
        import pytest
        errno = pytest.main([])
        sys.exit(errno)


setup(
    name="pyecoregen",
    version='0.0.1',
    description="Model to text framework for PyEcore, including the Ecore to Python generator",
    long_description=open('README.rst').read(),
    keywords="model metamodel EMF Ecore",
    url="https://github.com/pyecore/pyecoregen",
    author="Mike Pagel",
    author_email="mike@mpagel.de",

    packages=find_packages(),
    package_data={'': ['LICENSE', 'README.rst']},
    include_package_data=True,
    install_requires=['pyecore', 'pymultigen', 'jinja2', 'autopep8'],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},

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
