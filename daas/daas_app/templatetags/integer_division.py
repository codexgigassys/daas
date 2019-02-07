from django import template


register = template.Library()


@register.simple_tag
def integer_division(value, parts):
    value = float(value)
    parts = float(parts)
    return int(value / parts)
