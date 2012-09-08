# -*- coding: utf-8 -*-
from django import template
from fabric.api import env
from skwissh.models import Measure
import django
import skwissh

register = template.Library()


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
