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
    {% if a.derived %}_{% endif -%}
    {{ a.name }} = EAttribute({{ a | attrqualifiers }})
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_reference(r) -%}
    {{ r.name }} = EReference({{ r | refqualifiers }})
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_derived_attribute(d) -%}
    @property
    def {{ d.name }}(self):
        return self._{{ d.name }}

    {%- if d.changeable %}

    @{{ d.name }}.setter
    def {{ d.name }}(self, value):
        self._{{ d.name }} = value
    {% endif %}
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
    def __init__(self{{ generate_class_init_args(c) }}, **kwargs):
    {%- if not c.eSuperTypes %}
        if kwargs:
            raise AttributeError('unexpected arguments: {}'.format(kwargs))
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

{% if c.abstract %}@abstract
{% endif -%}
{{ generate_class_header(c) }}
{%- for a in c.eAttributes %}
    {{ generate_attribute(a) -}}
{% endfor %}
{%- for r in c.eReferences %}
    {{ generate_reference(r) -}}
{% endfor %}
{% if not user_module %}{% for d in c.eAttributes | selectattr('derived')  %}
    {{ generate_derived_attribute(d) }}
{% endfor %}{% endif %}
{{- generate_class_init(c) }}
{% if not user_module %}{% for o in c.eOperations %}
    {{ generate_operation(o) }}
{% endfor %}{% endif %}
{%- endmacro %}

{#- -------------------------------------------------------------------------------------------- -#}

{%- macro generate_mixin(c) %}

{{ generate_mixin_header(c) }}
{% for d in c.eAttributes | selectattr('derived')  %}
    {{ generate_derived_attribute(d) }}
{% endfor %}
{{- generate_mixin_init(c) }}
{% for o in c.eOperations %}
    {{ generate_operation(o) }}
{% endfor %}
{%- endmacro %}
