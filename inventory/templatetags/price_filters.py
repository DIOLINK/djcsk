from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def ars(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return mark_safe('<span class="text-gray-600">$&nbsp;—</span>')
    integer_part, decimal_part = f"{value:,.2f}".split(".")
    arg_format = (
        integer_part.replace(",", ".")
        + ","
        + decimal_part
    )
    return mark_safe(f'<span class="text-gray-600">$&nbsp;{arg_format}</span>')
