import typing
from django import template

register = template.Library()


@register.filter
def get(d: typing.Any, key: str, fallback: typing.Any = None) -> typing.Any:
    try:
        return getattr(d, key)
    except AttributeError:
        return d.get(key, fallback)
