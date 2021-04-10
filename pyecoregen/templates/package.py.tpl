{% if auto_register_package -%}
    from pyecore.resources import global_registry
{%- endif %}
from .{{ element.name }} import getEClassifier, eClassifiers
from .{{ element.name }} import name, nsURI, nsPrefix, eClass
{% if element.eClassifiers -%}
    from .{{ element.name }} import {{ element.eClassifiers | join(', ', attribute='name') }}
{%- endif %}

{% for package, classifs in imported_classifiers_package.items() -%}
    from {{ package|pyfqn }} import {{ classifs|map(attribute='name')|join(', ') }}
{% endfor -%}
{%- if not element.eSuperPackage %}
    {%- with %}
        {%- set all_references = element | all_contents(ecore.EReference) | list %}
        {%- set containing_types = all_references | map(attribute='eContainingClass') | list %}
        {%- set referenced_types = all_references | map(attribute='eType') | list %}
        {%- set types = containing_types + referenced_types | list %}
        {%- for sub in element | all_contents(ecore.EPackage) -%}
            {% set types_in_sub = types | selectattr('ePackage', 'sameas', sub) | set %}
            {%- if types_in_sub %}
from {{ sub | pyfqn(relative_to=1) }} import {{ types_in_sub | map(attribute='name') | join(', ') }}
            {%- endif -%}
        {% endfor -%}
    {% endwith -%}
{% endif %}
from . import {{ element.name }}

{%- if element.eSuperPackage %}
from .. import {{ element.eSuperPackage.name }}
{% endif %}

{%- for sub in element.eSubpackages %}
from . import {{ sub.name }}
{% endfor %}

__all__ = [{{ element.eClassifiers | map(attribute='name') | map('pyquotesingle') | join(', ') }}]

eSubpackages = [{{ element.eSubpackages | map(attribute='name') | join(', ') }}]
eSuperPackage = {{ element.eSuperPackage.name | default('None') }}
{{ element.name }}.eSubpackages = eSubpackages
{{ element.name }}.eSuperPackage = eSuperPackage
{% if not element.eSuperPackage %}
    {%- for e in element | all_contents(ecore.EReference) | rejectattr('eOpposite') %}
{{ e.eContainingClass.name }}.{{ e | derivedname }}.eType = {{ e.eType.name }}
    {%- endfor %}
    {%- with opposites = element | all_contents(ecore.EReference) | selectattr('eOpposite') | list %}
        {%- for e in opposites %}
{{ e.eContainingClass.name }}.{{ e | derivedname }}.eType = {{ e.eType.name }}
            {%- if e is opposite_before_self(opposites) %}
{{ e.eContainingClass.name }}.{{ e | derivedname }}.eOpposite = {{ e.eOpposite.eContainingClass.name }}.{{ e.eOpposite | derivedname }}
            {%- endif %}
        {%- endfor %}
    {%- endwith %}
{%- endif %}

otherClassifiers = [{{ element.eClassifiers | select('kind', ecore.EDataType) | map(attribute='name') | join(', ') }}]

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
{% if auto_register_package %}
register_packages = [{{ element.name }}] + eSubpackages
for pack in register_packages:
    global_registry[pack.nsURI] = pack

{% endif %}
