from django import template

register = template.Library()


@register.filter
def get(obj, key, fallback=None):
    try:
        return getattr(obj, key)
    except AttributeError:
        return obj.get(key, fallback)
