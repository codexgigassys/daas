from django import template


register = template.Library()


@register.simple_tag
def integer_division(value: str, parts: str) -> int:
    value = float(value)
    parts = float(parts)
    return int(value / parts)
