# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.core import serializers
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import utc
from django.views.decorators.cache import cache_page
from skwissh.forms import ServerForm
from skwissh.generic_views import get_server_list_context_data, \
    get_probe_list_context_data
from skwissh.models import Server, Measure, ServerGroup, Probe, MeasureDay, \
    MeasureWeek, MeasureMonth, GraphType
import datetime


###############################################################################
# Views
###############################################################################
@login_required
def index(request):
    return redirect('server-list')


def login_skwissh(request):
    return login(request, 'skwissh_login.html', extra_context={'skwissh_demo': getattr(settings, "SKWISSH_DEMO", False)})


@login_required
def server_list(request):
    return render(request, 'server-list.html', get_server_list_context_data())


@login_required
def probe_list(request):
    return render(request, 'probe-list.html', get_probe_list_context_data())


@login_required
def server_detail(request, server_id):
    try:
        server = Server.objects.get(pk=server_id)
    except:
        raise Http404

    form = ServerForm(instance=server)
    data = {
            'graphtypes': GraphType.objects.all(),
            'server_form': form,
            'server': server,
            'groups': ServerGroup.objects.all().order_by('name'),
            'nogroup_servers': Server.objects.filter(servergroup__isnull=True).order_by('hostname')
    }
    return render(request, 'server-detail.html', data)


###############################################################################
# Ajax
###############################################################################
@login_required
@cache_page(60)
def mesures(request, server_id, probe_id, period):
    if request.is_ajax():
        probe = get_object_or_404(Probe, pk=probe_id)
        server = get_object_or_404(Server, pk=server_id)
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if period == 'last':
            data = Measure.objects.filter(server=server, probe=probe)[0:1]
        elif period == 'hour':
            data = Measure.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(hours=1))
        elif period == 'day':
            data = MeasureDay.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(days=1))
        elif period == 'week':
            data = MeasureWeek.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(days=7))
        elif period == 'month':
            data = MeasureMonth.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(days=31))
        return HttpResponse(serializers.serialize('json', data), 'application/javascript')
    else:
        return HttpResponseServerError()
