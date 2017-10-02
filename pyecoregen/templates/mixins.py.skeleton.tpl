{% import 'module_utilities.tpl' as modutil with context -%}
"""Mixins to be implemented by user."""

{%- for c in classes -%}
{{ modutil.generate_mixin(c) }}
{%- endfor %}