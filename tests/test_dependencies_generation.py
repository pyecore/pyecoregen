import importlib
from os import path

import pytest

import pyecore.ecore as Ecore
from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
from pyecoregen.ecore import EcoreGenerator


@pytest.fixture(scope='module')
def generated_metamodel(pygen_output_dir):
    rset = ResourceSet()
    resource = rset.get_resource(URI('input/A.ecore'))
    library_model = resource.contents[0]
    generator = EcoreGenerator(with_dependencies=True)
    generator.generate(library_model, pygen_output_dir)
    return importlib.import_module('a')


def test_cross_resource_packages(generated_metamodel):
    A = generated_metamodel.A
    B = A.b.eType
    C = B.eClass.eSuperTypes[0].python_class
    A_package = A.eClass.ePackage
    B_package = B.eClass.ePackage
    C_package = C.eClass.ePackage
    assert A_package is not B_package
    assert A_package is not C_package
    assert B_package is not C_package
