# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from skwissh.generic_views import AddServerView, DeleteServerView, \
    UpdateServerView, DeleteGroupView, AddServerGroupView, UpdateServerGroupView, \
    DeleteProbeView, UpdateProbeView, AddProbeView, LogsView
from skwissh.models import CronLog, ServerGroup, Server

staff_required = user_passes_test(lambda u: u.is_staff)


urlpatterns = patterns('',
    # Skwissh index
    url(r'^$', 'skwissh.views.index', name='index'),

    # i18n
    url(r'^i18n/', include('django.conf.urls.i18n'), name="i18n"),

    # Login / logout.
    url(r'^login/$', 'skwissh.views.login_skwissh', name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"next_page": reverse_lazy('index')}),

    # Server
    url(r'^server-list/$', 'skwissh.views.server_list', name='server-list'),
    url(r'^server-detail/(\d+)/$', 'skwissh.views.server_detail', name='server-detail'),
    url(r'^add_server/$', staff_required(AddServerView.as_view()), name='add-server'),
    url(r'^delete_server/(?P<pk>[\w-]+)$', staff_required(DeleteServerView.as_view()), name='delete-server'),
    url(r'^update_server/(?P<pk>[\w-]+)$', staff_required(UpdateServerView.as_view()), name='update-server'),

    # Server Groups
    url(r'^add_group/$', staff_required(AddServerGroupView.as_view()), name='add-group'),
    url(r'^delete_group/(?P<pk>[\w-]+)$', staff_required(DeleteGroupView.as_view()), name='delete-group'),
    url(r'^update_group/$', staff_required(UpdateServerGroupView.as_view()), name='update-group'),

    # Probes
    url(r'^list_probe/$', 'skwissh.views.probe_list', name='probe-list'),
    url(r'^add_probe/$', staff_required(AddProbeView.as_view()), name='add-probe'),
    url(r'^update_probe/$', staff_required(UpdateProbeView.as_view()), name='update-probe'),
    url(r'^delete_probe/(?P<pk>[\w-]+)$', staff_required(DeleteProbeView.as_view()), name='delete-probe'),

    # Logs
    # url(r'^logs/$', CronLogListView.as_view(), name='logs-list'),
    url(r'^logs/$', login_required(LogsView.as_view()), name='logs-list'),

    # Ajax
    url(r'^mesures/(\d+)/(\d+)/(\w+)/$', 'skwissh.views.mesures', name='mesures'),

    # Ajax for Android
    url(r'^graphtypes/$', 'skwissh.views.graphtypes', name='graphtypes'),
    url(r'^server_groups/$', 'skwissh.views.server_groups', name='server-groups'),
    url(r'^servers/(\d+)/$', 'skwissh.views.servers', name='servers'),
    url(r'^sensors/(\d+)/$', 'skwissh.views.sensors', name='sensors'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^500/$', TemplateView.as_view(template_name='500.html')),
        url(r'^404/$', TemplateView.as_view(template_name='404.html')),
    )
