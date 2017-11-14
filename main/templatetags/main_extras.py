from django import template

register = template.Library()


@register.filter(name='float_to_percent')
def float_to_percent(value):
    return "{:.0%}".format(value)


@register.filter(name='dt_to_str')
def dt_to_str(value):
    return value.strftime('%Y-%m-%d')
