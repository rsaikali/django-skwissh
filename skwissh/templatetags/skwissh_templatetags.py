# -*- coding: utf-8 -*-
from django import template
from django.db.models.aggregates import Max
from django.utils import timezone
from fabfile import env
from skwissh.models import Measure
import django
import skwissh

register = template.Library()


@register.filter(name='addunits')
def addunits(value, units):
    return value.replace("@UNITS@", units)


@register.filter(name='addlegend')
def addlegend(value, labels):
    if labels:
        legend_options = "series:[ %s ]," % ",".join(["{label: '%s'}" % label for label in labels.split(';')])
        legend_options += "legend: {show: true, location: 'w', placement: 'inside'}"
        return value.replace("@SERIES@", legend_options)
    else:
        return value.replace("@SERIES@,", "")


@register.simple_tag(name='get_skwissh_version')
def get_skwissh_version():
    return str(skwissh.__version__)


@register.simple_tag(name='get_django_version')
def get_django_version():
    return str(django.get_version())


@register.simple_tag(name='get_fabric_version')
def get_fabric_version():
    return env.version


@register.simple_tag(name='get_nb_mesures')
def get_nb_mesures():
    return Measure.objects.count()


@register.simple_tag(name='get_last_mesure')
def get_last_mesure():
    try:
        last_mesure = Measure.objects.all().aggregate(Max('timestamp'))['timestamp__max'].astimezone(timezone.get_current_timezone()).strftime("%H:%M")
    except:
        last_mesure = ""
    return last_mesure
