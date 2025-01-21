from django import template

register = template.Library()


@register.filter
def get_range(value):
    return range(1, value + 1)


@register.filter
def get_range_from(value, arg):
    return range(value, arg + 1)


@register.filter
def split_by(value, separator):
    """
    Ділить рядок `value` по роздільнику `separator` і повертає список.
    Приклад використання в шаблоні:
        {% for item in "1,2,3,4"|split_by:"," %}
            {{ item }}
        {% endfor %}
    """
    return value.split(separator)
