from django import template

register = template.Library()


@register.filter
def people(querydict):
    people = querydict.get('people')

    return "" if people is None else people