"""Tests for the various features from the code generation templates."""
import importlib

import pytest

from pyecore.ecore import EPackage, EClass, EReference, EEnum, EAttribute, EInt, EOperation, \
    EParameter, EString, EDataType
from pyecoregen.ecore import EcoreGenerator


def generate_meta_model(model, output_dir):
    generator = EcoreGenerator()
    generator.generate(model, output_dir)
    return importlib.import_module(model.name)


def test_empty_package(pygen_output_dir):
    package = EPackage('empty')
    mm = generate_meta_model(package, pygen_output_dir)

    assert mm
    assert mm.name == 'empty'
    assert not mm.nsURI
    assert not mm.nsPrefix
    assert not mm.eClassifiers

    package.name = 'empty2'
    package.nsURI = 'http://xyz.org'
    package.nsPrefix = 'p'
    mm = generate_meta_model(package, pygen_output_dir)
    assert mm.nsURI == 'http://xyz.org'
    assert mm.nsPrefix == 'p'


def test_top_level_package_with_subpackages(pygen_output_dir):
    rootpkg = EPackage('rootpkg')
    subpkg = EPackage('subpkg')
    cls1 = EClass('A')
    cls2 = EClass('B')
    cls1.eStructuralFeatures.append(EReference('b', cls2))
    cls2.eStructuralFeatures.append(
        EReference('a', cls1, eOpposite=cls1.findEStructuralFeature('b')))
    rootpkg.eClassifiers.append(cls1)
    rootpkg.eSubpackages.append(subpkg)
    subpkg.eClassifiers.append(cls2)

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    assert mm.name == rootpkg.name
    assert mm.eSubpackages[0].eSuperPackage.name == rootpkg.name

    generated_A = mm.getEClassifier('A')
    assert generated_A

    generated_subpkg = mm.eSubpackages[0]
    assert generated_subpkg
    assert generated_subpkg.name == 'subpkg'

    generated_B = generated_subpkg.getEClassifier('B')
    assert generated_B

    a = generated_A()
    b = generated_B()
    a.b = b

    assert b.a is a


def test_package_with_enum(pygen_output_dir):
    enumpkg = EPackage('enumpkg')
    enum = EEnum('MyEnum', literals=('X', 'Y', 'Z'))
    enumpkg.eClassifiers.append(enum)

    mm = generate_meta_model(enumpkg, pygen_output_dir)

    generated_enum = mm.eClassifiers['MyEnum']
    assert isinstance(generated_enum, EEnum)
    assert set(l.name for l in generated_enum.eLiterals) == {'X', 'Y', 'Z'}


def test_classifier_imports(pygen_output_dir):
    # super types and enums from another package have to be imported in using module:
    rootpkg = EPackage('import_test')
    ppkg = EPackage('provider')
    upkg = EPackage('user')
    rootpkg.eSubpackages.extend([ppkg, upkg])

    super_class = EClass('SuperClass')
    enum = EEnum('AnEnum', literals=('A', 'B'))
    ppkg.eClassifiers.extend((super_class, enum))
    derived_class = EClass('DerivedClass', superclass=super_class)
    derived_class.eStructuralFeatures.append(EAttribute('kind', enum))
    upkg.eClassifiers.append(derived_class)

    # simply importing successully shows the imports have made the types visible
    mm = generate_meta_model(rootpkg, pygen_output_dir)
    assert mm


def test_class_with_features(pygen_output_dir):
    rootpkg = EPackage('class_features')
    class_ = EClass('MyClass')
    rootpkg.eClassifiers.append(class_)
    class_.eStructuralFeatures.append(EAttribute('number', EInt, changeable=False))
    class_.eStructuralFeatures.append(EReference('ref', class_))

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    generated_class = mm.eClassifiers['MyClass']
    instance = generated_class(number=7)
    assert instance.number == 7
    assert not instance.ref

    instance.ref = instance
    assert instance.ref is instance


def test_operation(pygen_output_dir):
    rootpkg = EPackage('operation')
    class_ = EClass('MyClass')
    rootpkg.eClassifiers.append(class_)
    class_.eOperations.append(EOperation(
        'do_it',
        EInt,
        params=(EParameter('p1', EInt, required=True), EParameter('p2', EInt)),
    ))

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    instance = mm.eClassifiers['MyClass']()

    with pytest.raises(NotImplementedError):
        instance.do_it(1, 2)

    # missing non-required argument
    with pytest.raises(NotImplementedError):
        instance.do_it(1)

    # missing non-required argument
    with pytest.raises(NotImplementedError):
        instance.do_it(p1=1)

    # missing required argument:
    with pytest.raises(TypeError):
        instance.do_it(p2=2)


def test_class_with_derived_features(pygen_output_dir):
    rootpkg = EPackage('simpleClasses')
    MyClass = EClass('MyClass')
    rootpkg.eClassifiers.append(MyClass)
    any_feature = EAttribute('any', EString, derived=True)
    MyClass.eStructuralFeatures.append(any_feature)

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    generated_class = mm.eClassifiers['MyClass']

    assert mm.MyClass is generated_class
    assert isinstance(mm.MyClass._any, EAttribute)
    assert mm.MyClass._any.derived is True
    assert mm.MyClass._any.name == 'any'


def test_various_datatypes(pygen_output_dir):
    rootpkg = EPackage('datatypes')
    data1 = EDataType('Data1', instanceClassName='java.lang.Integer')
    data2 = EDataType('Data2', instanceClassName='Unknown')
    rootpkg.eClassifiers.extend([data1, data2])

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    gendata1 = mm.eClassifiers['Data1']
    gendata2 = mm.eClassifiers['Data2']

    assert gendata1 is mm.Data1
    assert mm.Data1.eType is int
    assert mm.Data1.default_value is 0
    assert gendata2 is mm.Data2
    assert mm.Data2.eType is object
    assert isinstance(mm.Data2.default_value, object)


def test_class_with_feature_many(pygen_output_dir):
    rootpkg = EPackage('manyfeatures')
    MyClass = EClass('MyClass')
    rootpkg.eClassifiers.append(MyClass)
    any_feature = EAttribute('any', EString, upper=-1)
    MyClass.eStructuralFeatures.append(any_feature)

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    generated_class = mm.eClassifiers['MyClass']
    instance = mm.MyClass()

    assert generated_class is mm.MyClass
    assert isinstance(mm.MyClass.any, EAttribute)
    assert instance.any == set()
