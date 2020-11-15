{%- macro generate_enum(e) %}
{{ e.name }} = EEnum('{{ e.name }}', literals=[{{ e.eLiterals | map(attribute='name') | map('pyquotesingle') | join(', ') }}])
{% endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_edatatype(e) %}
{{ e.name }} = EDataType('{{ e.name }}', instanceClassName='{{ e.instanceClassName }}')
{% endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_class_header(c) -%}
class {{ c.name }}(
    {%- if user_module %}_user_module.{{ c.name }}Mixin, {% endif -%}
    {{ c | supertypes -}}
):
    {{ c | docstringline -}}
{% endmacro -%}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_mixin_header(c) -%}
class {{ c.name }}Mixin:
    """User defined mixin class for {{ c.name }}."""
{% endmacro -%}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_attribute(a) -%}
    {{ a | derivedname }} = EAttribute({{ a | attrqualifiers }}
                                      {%- if a.derived and a.many %}, {{ generate_derived_fragment(a) }}{% endif %})
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_reference(r) -%}
    {{ r | derivedname }} = EReference({{ r | refqualifiers }}
                                      {%- if r.derived and r.many %}, {{ generate_derived_fragment(r) }}{% endif %})
{%- endmacro %}

{%- macro generate_derived_fragment(f) -%}
derived_class={% if user_module %}_user_module.{% endif %}Derived{{ f.name | capitalize }}
{%- endmacro -%}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_derived_single(d) -%}
    @property
    def {{ d.name }}(self):
        raise NotImplementedError('Missing implementation for {{ d.name }}')

    {%- if d.changeable %}

    @{{ d.name }}.setter
    def {{ d.name }}(self, value):
        raise NotImplementedError('Missing implementation for {{ d.name }}')
    {% endif %}
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_derived_collection(d) -%}

class Derived{{ d.name | capitalize }}(EDerivedCollection):
    pass
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_class_init_args(c) -%}
    {% if c.eStructuralFeatures %}, *, {% endif -%}
    {{ c.eStructuralFeatures | map(attribute='name') | map('re_sub', '$', '=None') | join(', ') }}
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_feature_init(feature) %}
    {%- if feature.upperBound == 1 %}
        if {{ feature.name }} is not None:
            self.{{ feature.name }} = {{ feature.name }}
    {%- else %}
        if {{ feature.name }}:
            self.{{ feature.name }}.extend({{ feature.name }})
    {%- endif %}
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_class_init(c) %}
    def __init__(self{{ generate_class_init_args(c) }}{% if c.eSuperTypes %}, **kwargs{% endif %}):
    {%- if not c.eSuperTypes %}
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))
    {%- endif %}

        super().__init__({% if c.eSuperTypes %}**kwargs{% endif %})
    {%- for feature in c.eStructuralFeatures | reject('type', ecore.EReference) %}
    {{ generate_feature_init(feature) }}
    {%- endfor %}
    {%- for feature in c.eStructuralFeatures | select('type', ecore.EReference) %}
    {{ generate_feature_init(feature) }}
    {%- endfor %}
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_mixin_init(c) %}
    def __init__(self{{ generate_class_init_args(c) }}, **kwargs):
        super().__init__({% if c.eSuperTypes %}**kwargs{% endif %})
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_operation_args(o) -%}
    {% for p in o.eParameters -%}
        , {{ p.name }}{% if not p.required %}=None{% endif -%}
    {% endfor -%}
{%- endmacro  %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_operation(o) %}
    def {{ o.name }}(self{{ generate_operation_args(o) }}):
        {{ o | docstringline }}
        raise NotImplementedError('operation {{ o.name }}(...) not yet implemented')
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_class(c) %}

{% if not user_module %}{% for d in c.eStructuralFeatures | selectattr('derived') | selectattr('many') %}
{{ generate_derived_collection(d) }}
{% endfor %}{% endif %}

{% if c.abstract %}@abstract
{% endif -%}
{{ generate_class_header(c) }}
{%- for a in c.eAttributes %}
    {{ generate_attribute(a) -}}
{% endfor %}
{%- for r in c.eReferences %}
    {{ generate_reference(r) -}}
{% endfor %}
{% if not user_module %}{% for d in c.eStructuralFeatures | selectattr('derived') | rejectattr('many') %}
    {{ generate_derived_single(d) }}
{% endfor %}{% endif %}
{{- generate_class_init(c) }}
{% if not user_module %}{% for o in c.eOperations %}
    {{ generate_operation(o) }}
{% endfor %}{% endif %}
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_mixin(c) %}

{% for d in c.eStructuralFeatures | selectattr('derived') | selectattr('many')  %}
{{ generate_derived_collection(d) }}
{% endfor %}

{{ generate_mixin_header(c) }}
{% for d in c.eStructuralFeatures | selectattr('derived') | rejectattr('many') %}
    {{ generate_derived_single(d) }}
{% endfor %}
{{- generate_mixin_init(c) }}
{% for o in c.eOperations %}
    {{ generate_operation(o) }}
{% endfor %}
{%- endmacro %}
