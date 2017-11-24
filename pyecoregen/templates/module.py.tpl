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
{{ modutil.generate_enum(c) }}
{%- endfor %}
{% for c in element.eClassifiers if c is type(ecore.EDataType) -%}
{{ modutil.generate_edatatype(c) }}
{%- endfor %}

{%- for c in classes -%}
{{ modutil.generate_class(c) }}
{%- endfor %}
