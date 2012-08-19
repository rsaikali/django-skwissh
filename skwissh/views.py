# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse_lazy
from django.forms.models import modelformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from extra_views.formsets import ModelFormSetView
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


@login_required
def server_list(request):
    ServerGroupFormSet = modelformset_factory(ServerGroup, form=ServerGroupForm)
    data = {
            'server_form': ServerForm(),
            'server_group_form': ServerGroupForm(),
            'server_group_formset': ServerGroupFormSet(queryset=ServerGroup.objects.all().select_related()),
            'groups': ServerGroup.objects.all().order_by('name'),
            'nogroup_servers': Server.objects.filter(servergroup__isnull=True).order_by('hostname')
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
    server = Server.objects.get(pk=server_id)
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
        now = datetime.datetime.now()
        now = now - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)
        if period == 'last':           # Each minute
            data = Measure.objects.filter(server=server_id, probe=probe_id)[0:1]
        elif period == 'hour':         # Each minute
            data = Measure.objects.filter(server=server_id, probe=probe_id, timestamp__gte=now - datetime.timedelta(hours=1))
        elif period == 'day':          # Each 5 minutes
            data = MeasureDay.objects.filter(server=server_id, probe=probe_id, timestamp__gte=now - datetime.timedelta(days=1))
        elif period == 'week':         # Each 30 minutes
            data = MeasureWeek.objects.filter(server=server_id, probe=probe_id, timestamp__gte=now - datetime.timedelta(days=7))
        elif period == 'month':        # Each hour
            data = MeasureMonth.objects.filter(server=server_id, probe=probe_id, timestamp__gte=now - datetime.timedelta(days=31))
        return HttpResponse(serializers.serialize('json', data), 'application/javascript')
    else:
        raise Http404


###############################################################################
# Generic views
###############################################################################

#------------------------------------------------------------------------------
# Server
#------------------------------------------------------------------------------
class AddServerView(CreateView):
    model = Server
    form_class = ServerForm

    def get_success_url(self):
        return reverse_lazy('server-list')


class UpdateServerView(UpdateView):
    model = Server
    form_class = ServerForm


class DeleteServerView(DeleteView):
    model = Server

    def get_success_url(self):
        return reverse_lazy('server-list')


#------------------------------------------------------------------------------
# Server Group
#------------------------------------------------------------------------------
class AddServerGroupView(CreateView):
    model = ServerGroup
    form_class = ServerGroupForm

    def get_success_url(self):
        return reverse_lazy('server-list')


class UpdateServerGroupView(ModelFormSetView):
    model = ServerGroup
    form_class = ServerGroupForm
    success_url = reverse_lazy('server-list')


class DeleteGroupView(DeleteView):
    model = ServerGroup

    def get_success_url(self):
        return reverse_lazy('server-list')


#------------------------------------------------------------------------------
# Probes
#------------------------------------------------------------------------------
class AddProbeView(CreateView):
    model = Probe
    form_class = ProbeForm

    def get_success_url(self):
        return reverse_lazy('probe-list')


class UpdateProbeView(ModelFormSetView):
    model = Probe
    form_class = ProbeForm
    success_url = reverse_lazy('probe-list')


class DeleteProbeView(DeleteView):
    model = Probe

    def get_success_url(self):
        return reverse_lazy('probe-list')
