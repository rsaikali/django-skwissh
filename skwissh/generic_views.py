# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.forms.models import modelformset_factory
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
    template_name = 'server-list.html'

    def get_success_url(self):
        return reverse_lazy('server-list')

    def get_context_data(self, **kwargs):
        context = super(AddServerView, self).get_context_data(**kwargs)
        context.update(get_server_list_context_data())
        context['server_form'] = context['form']
        return context


class UpdateServerView(UpdateView):
    model = Server
    form_class = ServerForm
    template_name = 'server-detail.html'


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
    template_name = 'server-list.html'

    def get_success_url(self):
        return reverse_lazy('server-list')

    def get_context_data(self, **kwargs):
        context = super(AddServerGroupView, self).get_context_data(**kwargs)
        context.update(get_server_list_context_data())
        context['server_group_form'] = context['form']
        return context


class UpdateServerGroupView(ModelFormSetView):
    model = ServerGroup
    form_class = ServerGroupForm
    success_url = reverse_lazy('server-list')
    template_name = 'server-list.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateServerGroupView, self).get_context_data(**kwargs)
        context.update(get_server_list_context_data())
        context['server_group_formset'] = context['formset']
        return context


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
    template_name = 'probe-list.html'

    def get_success_url(self):
        return reverse_lazy('probe-list')

    def get_context_data(self, **kwargs):
        context = super(AddProbeView, self).get_context_data(**kwargs)
        context.update(get_probe_list_context_data())
        context['probe_form'] = context['form']
        return context


class UpdateProbeView(ModelFormSetView):
    model = Probe
    form_class = ProbeForm
    success_url = reverse_lazy('probe-list')
    template_name = 'probe-list.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateProbeView, self).get_context_data(**kwargs)
        context.update(get_probe_list_context_data())
        context['probe_formset'] = context['formset']
        return context


class DeleteProbeView(DeleteView):
    model = Probe

    def get_success_url(self):
        return reverse_lazy('probe-list')


#------------------------------------------------------------------------------
# Context data
#------------------------------------------------------------------------------
def get_server_list_context_data():
    ServerGroupFormSet = modelformset_factory(ServerGroup, form=ServerGroupForm)
    return {
            'server_form': ServerForm(),
            'server_group_form': ServerGroupForm(),
            'server_group_formset': ServerGroupFormSet(queryset=ServerGroup.objects.all().select_related()),
            'groups': ServerGroup.objects.all().order_by('name'),
            'nogroup_servers': Server.objects.filter(servergroup__isnull=True).order_by('hostname'),
    }


def get_probe_list_context_data():
    ProbeFormSet = modelformset_factory(Probe, form=ProbeForm)
    return {
            'probe_form': ProbeForm(),
            'probe_formset': ProbeFormSet(queryset=Probe.objects.all().select_related()),
            'probes': Probe.objects.all(),
            'groups': ServerGroup.objects.all().order_by('name'),
            'nogroup_servers': Server.objects.filter(servergroup__isnull=True).order_by('hostname')
    }
