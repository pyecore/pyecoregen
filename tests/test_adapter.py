from pyecore import ecore
from pyecoregen.adapter import adapt_name


def test__name_adapter():
    p = ecore.EPackage('MyPackage')

    c1 = ecore.EClass('MyClass')
    p.eClassifiers.append(c1)
    a1 = ecore.EAttribute('att', ecore.EString, upper=-1)
    c1.eStructuralFeatures.append(a1)

    c2 = ecore.EClass('pass')
    p.eClassifiers.append(c2)
    a2 = ecore.EAttribute('else', ecore.EString, upper=-1)
    c2.eStructuralFeatures.append(a2)

    assert c2.name == 'pass'
    assert a2.name == 'else'

    with adapt_name():
        assert c1.name == 'MyClass'
        assert a1.name == 'att'
        assert c2.name == 'pass_'
        assert a2.name == 'else_'

    assert c2.name == 'pass'
    assert a2.name == 'else'


