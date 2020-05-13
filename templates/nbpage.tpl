{% extends 'full.tpl'%}
{% block any_cell %}
{% if cell['metadata'].get('tags', []) %}
    <div style="background-color:white; border:thin solid white; color:red">
    Tags:&nbsp;
    {% for tag in cell['metadata'].get('tags', []) %}
        {{ tag }} &nbsp;
    {% endfor %}
    </div>
    <div style="border:thin solid gray">
        {{ super() }}
    </div>
{% else %}
    {{ super() }}
{% endif %}
{% endblock any_cell %}