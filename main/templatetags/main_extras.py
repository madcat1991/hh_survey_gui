from django import template
from django.conf import settings

register = template.Library()


@register.filter(name='float_to_percent')
def float_to_percent(value):
    return "{:.0%}".format(value)


@register.filter(name='dt_to_str')
def dt_to_str(value):
    return value.strftime('%Y-%m-%d')


@register.filter(name='hh_uri_to_url')
def hh_uri_to_url(value):
    if value is not None:
        return settings.HH_URL + value
    return None


@register.filter(name='hh_image_uri_to_url')
def hh_image_uri_to_url(value):
    if value is not None:
        return settings.HH_IMAGE_URL + value
    return settings.HH_DEFAULT_IMAGE_URL
