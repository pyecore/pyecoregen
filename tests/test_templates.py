"""Tests for the various features from the code generation templates."""
import importlib
from unittest import mock

import pytest

from pyecore.ecore import EPackage, EClass, EReference, EEnum, EAttribute, EInt, EOperation, \
    EParameter, EString, EDataType, EAnnotation
from pyecoregen.ecore import EcoreGenerator
from user_provided.module import MyClassMixin, \
    MyOtherClassMixin  # search path set in test configuration


def generate_meta_model(model, output_dir, *, user_module=None, auto_register_package=None):
    generator = EcoreGenerator(user_module=user_module, auto_register_package=auto_register_package)
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


def test_class_with_documentation(pygen_output_dir):
    rootpkg = EPackage('class_doc')
    class_ = EClass('MyClass')
    rootpkg.eClassifiers.append(class_)

    doc = EAnnotation('http://www.eclipse.org/emf/2002/GenModel')
    class_.eAnnotations.append(doc)
    doc.details['documentation'] = 'This is a documentation test'

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    generated_class = mm.eClassifiers['MyClass']
    assert generated_class.__doc__ == 'This is a documentation test'


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
    data1 = EDataType('Data1', instanceClassName='int')
    data2 = EDataType('Data2', instanceClassName='Unknown')
    data3 = EDataType('Data3', instanceClassName='java.lang.Integer')
    rootpkg.eClassifiers.extend([data1, data2, data3])

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    gendata1 = mm.eClassifiers['Data1']
    gendata2 = mm.eClassifiers['Data2']
    gendata3 = mm.eClassifiers['Data3']

    assert gendata1 is mm.Data1
    assert mm.Data1.eType is int
    assert mm.Data1.default_value is 0
    assert gendata2 is mm.Data2
    assert mm.Data2.eType is object
    assert isinstance(mm.Data2.default_value, object)
    assert gendata3 is mm.Data3
    assert mm.Data3.eType is int
    assert mm.Data3.default_value is None


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


def test_pythonic_names(pygen_output_dir):
    rootpkg = EPackage('pythonic_names')

    c1 = EClass('MyClass')
    rootpkg.eClassifiers.append(c1)
    a1 = EAttribute('att', EString, upper=-1)
    c1.eStructuralFeatures.append(a1)

    c2 = EClass('pass')
    rootpkg.eClassifiers.append(c2)
    a2 = EAttribute('else', EString, upper=-1)
    c2.eStructuralFeatures.append(a2)

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    assert mm.eClassifiers['MyClass'] is mm.MyClass
    assert mm.eClassifiers['pass_'] is mm.pass_
    assert isinstance(mm.pass_.else_, EAttribute)
    assert mm.pass_().else_ == set()


def test_attribute_with_feature_id(pygen_output_dir):
    rootpkg = EPackage('id_attribute')
    c1 = EClass('MyClass')
    rootpkg.eClassifiers.append(c1)

    a1 = EAttribute('att', EString, iD=True)
    a2 = EAttribute('att2', EString)
    c1.eStructuralFeatures.extend([a1, a2])

    mm = generate_meta_model(rootpkg, pygen_output_dir)
    assert isinstance(mm.MyClass.att, EAttribute)
    assert isinstance(mm.MyClass.att2, EAttribute)
    assert mm.MyClass.att.iD is True
    assert mm.MyClass.att2.iD is False


def test_eoperation_with_documentation(pygen_output_dir):
    rootpkg = EPackage('eoperation_with_documentation')
    c1 = EClass('MyClass')
    rootpkg.eClassifiers.append(c1)

    operation = EOperation('do_it')
    doc = EAnnotation('http://www.eclipse.org/emf/2002/GenModel')
    operation.eAnnotations.append(doc)
    doc.details['documentation'] = 'This is a documentation test'
    c1.eOperations.append(operation)

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    instance = mm.MyClass()
    with pytest.raises(NotImplementedError):
        instance.do_it()


def test_eattribute_derived_not_changeable(pygen_output_dir):
    rootpkg = EPackage('changeable_attribute')
    c1 = EClass('MyClass')
    rootpkg.eClassifiers.append(c1)

    att1 = EAttribute('att1', EString, derived=True, changeable=True)
    att2 = EAttribute('att2', EString, derived=True, changeable=False)

    c1.eStructuralFeatures.extend([att2, att1])

    mm = generate_meta_model(rootpkg, pygen_output_dir)

    instance = mm.MyClass()
    assert instance.att1 is None
    assert instance.att2 is None

    instance.att1 = "test_value"
    assert instance.att1 == "test_value"

    with pytest.raises(AttributeError):
        instance.att2 = "test_value2"


def test_auto_registration_enabled(pygen_output_dir):
    rootpkg = EPackage('auto_registration', nsURI='http://autoregister')
    c1 = EClass('MyClass')
    rootpkg.eClassifiers.append(c1)

    mm = generate_meta_model(rootpkg, pygen_output_dir, auto_register_package=True)

    from pyecore.resources import global_registry
    assert mm.nsURI in global_registry
    assert global_registry[mm.nsURI] is mm.auto_registration


def test_user_module_imported(pygen_output_dir):
    rootpkg = EPackage('user_module')
    c1 = EClass('MyClass')
    rootpkg.eClassifiers.append(c1)

    with pytest.raises(ImportError) as ex:
        mm = generate_meta_model(rootpkg, pygen_output_dir, user_module='some_module')
        assert 'some_module' in ex.message


def test_user_module_derived_from_mixin(pygen_output_dir):
    rootpkg = EPackage('derived_from_mixin')
    c1 = EClass('MyClass')
    c1.eOperations.append(EOperation('do_it'))
    c1.eStructuralFeatures.append(EAttribute('any', EString, derived=True))
    rootpkg.eClassifiers.append(c1)
    c2 = EClass('MyOtherClass')
    c2.eStructuralFeatures.append(EAttribute('other', EString, derived=True))
    c2.eSuperTypes.append(c1)
    rootpkg.eClassifiers.append(c2)

    mm = generate_meta_model(rootpkg, pygen_output_dir, user_module='user_provided.module')

    c = mm.MyOtherClass(any='any', other='other')
    assert isinstance(c, MyClassMixin)
    assert isinstance(c, MyOtherClassMixin)
    assert isinstance(c, mm.MyClass)
    assert c.any == 'any'
    c.mock_other.assert_called_once_with('other')

    assert not c.do_it.called
    c.do_it()
    assert c.do_it.called
