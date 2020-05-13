{% extends 'full.tpl'%}
{% block any_cell %}
{% if cell['metadata'].get('tags', []) %}
    <div style="background-color:white; border:thin solid grey; color:red">
    &nbsp;
    {% for tag in cell['metadata'].get('tags', []) %}
        <a href="https://jckantor.github.io/nbpages/tag_index.html?flush=true">{{ tag }}</a> &nbsp;
    {% endfor %}
    </div>
    <div style="border:thin solid white;">
        {{ super() }}
    </div>
{% else %}
    {{ super() }}
{% endif %}
{% endblock any_cell %}