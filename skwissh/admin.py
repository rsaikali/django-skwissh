# -*- coding: utf-8 -*-
from django.contrib import admin
from skwissh.forms import ServerForm
from skwissh.models import Probe, Server, Measure, ServerGroup, GraphType, \
    MeasureDay, MeasureWeek, MeasureMonth


class GraphTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(GraphType, GraphTypeAdmin)


class ServerGroupAdmin(admin.ModelAdmin):
    pass
admin.site.register(ServerGroup, ServerGroupAdmin)


class ServerAdmin(admin.ModelAdmin):
    form = ServerForm
admin.site.register(Server, ServerAdmin)


class ProbeAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'ssh_command', 'date_created', 'date_modified')
admin.site.register(Probe, ProbeAdmin)


class MeasureAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'server', 'probe', 'value')
admin.site.register(Measure, MeasureAdmin)
admin.site.register(MeasureDay, MeasureAdmin)
admin.site.register(MeasureWeek, MeasureAdmin)
admin.site.register(MeasureMonth, MeasureAdmin)
