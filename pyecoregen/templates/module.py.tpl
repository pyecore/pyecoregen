{% import 'module_utilities.tpl' as modutil with context -%}
"""Definition of meta model '{{ element.name }}'."""
from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import *
{% for package, classifs in imported_classifiers.items() -%}
    from {{ package|pyfqn }} import {{ classifs|map(attribute='name')|join(', ') }}
{% endfor -%}
{% if user_module -%}
    import {{ user_module }} as _user_module
{% endif %}

name = '{{ element.name }}'
nsURI = '{{ element.nsURI | default(boolean=True) }}'
nsPrefix = '{{ element.nsPrefix | default(boolean=True) }}'

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)

{%- for c in element.eClassifiers if c is type(ecore.EEnum) -%}
{% if loop.first and textX %}
class EEnum(Ecore.EEnum):

    def __init__(self, name=None, default_value=None, literals=None, **kwargs):
        super().__init__(name, default_value, literals)
        self.__dict__.update(kwargs)

    @property
    def value(self):
        ''' returns the value of the attribute '''
        for attr in [a for a in self.__dict__ if
                     not a.startswith('__') and not
                     a.startswith('_tx_')]:
            obj = getattr(self, attr)
            if obj and isinstance(obj, str):
                return obj
{% endif %}
{{ modutil.generate_enum(c) }}
{%- endfor %}
{% for c in element.eClassifiers if c is type(ecore.EDataType) -%}
{% if loop.first and textX %}
class EDataType(Ecore.EDataType):

    def __new__(cls, *args, **kwargs):
        self = Ecore.EDataType.__new__(cls, *args, **kwargs)
        self.__name__ = args[0]
        return self

{% endif %}
{{ modutil.generate_edatatype(c) }}
{%- endfor %}

{%- for c in classes -%}
{% if loop.first and textX %}
class EObject(Ecore.EObject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key in kwargs:
            if self.__dict__.get(key, False):
                continue
            setattr(self, key, kwargs[key])

{% endif %}
{{ modutil.generate_class(c) }}
{%- endfor %}
