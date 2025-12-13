from django import template

register = template.Library()


@register.filter
def dictget(dictionary, key):
    """딕셔너리에서 키로 값을 가져옴"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def split(value, delimiter=','):
    """문자열을 구분자로 분리"""
    if value:
        return value.split(delimiter)
    return []


@register.filter
def percentage(value, total):
    """백분율 계산"""
    try:
        return int((float(value) / float(total)) * 100)
    except (ValueError, ZeroDivisionError):
        return 0
