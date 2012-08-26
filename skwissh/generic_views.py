# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from extra_views.formsets import ModelFormSetView
from skwissh.forms import ServerForm, ServerGroupForm, ProbeForm
from skwissh.models import Server, ServerGroup, Probe


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
