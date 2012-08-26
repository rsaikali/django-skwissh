# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.core import serializers
from django.forms.models import modelformset_factory
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import render, redirect
from django.utils.timezone import utc
from django.views.decorators.cache import cache_page
from skwissh.forms import ServerForm, ServerGroupForm, ProbeForm
from skwissh.models import Server, Measure, ServerGroup, Probe, MeasureDay, \
    MeasureWeek, MeasureMonth
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
    ServerGroupFormSet = modelformset_factory(ServerGroup, form=ServerGroupForm)
    data = {
            'server_form': ServerForm(),
            'server_group_form': ServerGroupForm(),
            'server_group_formset': ServerGroupFormSet(queryset=ServerGroup.objects.all().select_related()),
            'groups': ServerGroup.objects.all().order_by('name'),
            'nogroup_servers': Server.objects.filter(servergroup__isnull=True).order_by('hostname'),
    }
    return render(request, 'server-list.html', data)


@login_required
def probe_list(request):
    ProbeFormSet = modelformset_factory(Probe, form=ProbeForm)
    data = {
            'probe_form': ProbeForm(),
            'probe_formset': ProbeFormSet(queryset=Probe.objects.all().select_related()),
            'probes': Probe.objects.all(),
            'groups': ServerGroup.objects.all().order_by('name'),
            'nogroup_servers': Server.objects.filter(servergroup__isnull=True).order_by('hostname')
    }
    return render(request, 'probe-list.html', data)


@login_required
def server_detail(request, server_id):
    try:
        server = Server.objects.get(pk=server_id)
    except:
        raise Http404

    form = ServerForm(instance=server)
    data = {
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
        try:
            probe = Probe.objects.get(id=probe_id)
            server = Server.objects.get(id=server_id)
        except:
            raise Http404

        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        now = now - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)
        if period == 'last':           # Each minute
            data = Measure.objects.filter(server=server, probe=probe)[0:1]
        elif period == 'hour':         # Each minute
            data = Measure.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(hours=1))
        elif period == 'day':          # Each 5 minutes
            data = MeasureDay.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(days=1))
        elif period == 'week':         # Each 30 minutes
            data = MeasureWeek.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(days=7))
        elif period == 'month':        # Each hour
            data = MeasureMonth.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(days=31))
        return HttpResponse(serializers.serialize('json', data), 'application/javascript')
    else:
        return HttpResponseServerError()
