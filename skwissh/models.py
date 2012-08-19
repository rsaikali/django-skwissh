# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime


class GraphType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u"Nom"), null=True, blank=True)
    options = models.TextField(verbose_name=_(u"Options jqPlot"), null=True, blank=True)
    date_created = models.DateTimeField(verbose_name=_(u"Date de création"), null=True, auto_now_add=True, default=datetime.datetime.now())
    date_modified = models.DateTimeField(verbose_name=_(u"Date de modification"), null=True, auto_now=True, default=datetime.datetime.now())

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = u"type de graphique"
        verbose_name_plural = u"types de graphiques"


def get_default_graph_type():
    return GraphType.objects.get(name="linegraph")


class Probe(models.Model):
    display_name = models.CharField(max_length=255, verbose_name=_(u"Nom de la sonde"), null=True, blank=True)
    addon_name = models.CharField(max_length=255, verbose_name=_(u"Infos complémentaires (version linux...)"), null=True, blank=True)
    ssh_command = models.TextField(verbose_name=_(u"Commande SSH"), null=True, blank=True)
    use_sudo = models.BooleanField(verbose_name=_(u"Utilise 'sudo' ?"), default=False)
    python_parse = models.TextField(verbose_name=_(u"Commande Python de parsing"), null=True, blank=True, default="output = output")
    graph_type = models.ForeignKey(GraphType, verbose_name=_(u"Type de visualisation"), default=get_default_graph_type)
    probe_unit = models.CharField(max_length=10, verbose_name=_(u"Unité"), null=True, blank=True)
    probe_labels = models.CharField(max_length=255, verbose_name=_(u"Labels des valeurs"), null=True, blank=True)
    date_created = models.DateTimeField(verbose_name=_(u"Date de création"), null=True, auto_now_add=True, default=datetime.datetime.now())
    date_modified = models.DateTimeField(verbose_name=_(u"Date de modification"), null=True, auto_now=True, default=datetime.datetime.now())

    def __unicode__(self):
        if self.addon_name:
            return u"%s (%s)" % (self.display_name, self.addon_name)
        else:
            return u"%s" % self.display_name

    class Meta:
        verbose_name = u"sonde"
        ordering = ['display_name', 'addon_name']


class Server(models.Model):
    hostname = models.CharField(max_length=255, verbose_name=_(u"Nom du serveur"))
    ip = models.IPAddressField(verbose_name=_(u"Adresse IP"), null=True, blank=True)
    state = models.BooleanField(verbose_name=_(u"Serveur accessible ?"), default=False)
    username = models.CharField(max_length=50, verbose_name=_(u"Nom d'utilisateur SSH"), null=True, blank=True, default="")
    password = models.CharField(max_length=50, verbose_name=_(u"Mot de passe SSH"), null=True, blank=True, default="")
    date_created = models.DateTimeField(verbose_name=_(u"Date de création"), null=True, auto_now_add=True, default=datetime.datetime.now())
    date_modified = models.DateTimeField(verbose_name=_(u"Date de modification"), null=True, auto_now=True, default=datetime.datetime.now())
    probes = models.ManyToManyField(Probe, verbose_name=_(u"Sondes"), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.hostname

    @models.permalink
    def get_absolute_url(self):
        return ('server-detail', [self.id])

    class Meta:
        verbose_name = u"serveur"
        ordering = ['hostname', 'ip']


class ServerGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u"Nom du groupe"))
    date_created = models.DateTimeField(verbose_name=_(u"Date de création"), null=True, auto_now_add=True, default=datetime.datetime.now())
    date_modified = models.DateTimeField(verbose_name=_(u"Date de modification"), null=True, auto_now=True, default=datetime.datetime.now())
    servers = models.ManyToManyField(Server, verbose_name=_(u"Serveurs"), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = u"groupe de serveurs"
        verbose_name_plural = u"groupes de serveurs"
        ordering = ['name']


class Measure(models.Model):
    timestamp = models.DateTimeField(verbose_name=_(u"Date et heure"))
    server = models.ForeignKey(Server, verbose_name=_(u"Serveur"))
    probe = models.ForeignKey(Probe, verbose_name=_(u"Sonde"))
    value = models.CharField(max_length=4096, verbose_name=_(u"Valeur mesurée"))

    def __unicode__(self):
        return u"%s" % self.value

    class Meta:
        verbose_name = "mesure"
        ordering = ['-timestamp', 'server', 'probe']


class MeasureDay(models.Model):
    timestamp = models.DateTimeField(verbose_name=_(u"Date et heure"))
    server = models.ForeignKey(Server, verbose_name=_(u"Serveur"))
    probe = models.ForeignKey(Probe, verbose_name=_(u"Sonde"))
    value = models.CharField(max_length=4096, verbose_name=_(u"Valeur mesurée"))

    def __unicode__(self):
        return u"%s" % self.value

    class Meta:
        verbose_name = "mesureDay"
        ordering = ['-timestamp', 'server', 'probe']


class MeasureWeek(models.Model):
    timestamp = models.DateTimeField(verbose_name=_(u"Date et heure"))
    server = models.ForeignKey(Server, verbose_name=_(u"Serveur"))
    probe = models.ForeignKey(Probe, verbose_name=_(u"Sonde"))
    value = models.CharField(max_length=4096, verbose_name=_(u"Valeur mesurée"))

    def __unicode__(self):
        return u"%s" % self.value

    class Meta:
        verbose_name = "mesureWeek"
        ordering = ['-timestamp', 'server', 'probe']


class MeasureMonth(models.Model):
    timestamp = models.DateTimeField(verbose_name=_(u"Date et heure"))
    server = models.ForeignKey(Server, verbose_name=_(u"Serveur"))
    probe = models.ForeignKey(Probe, verbose_name=_(u"Sonde"))
    value = models.CharField(max_length=4096, verbose_name=_(u"Valeur mesurée"))

    def __unicode__(self):
        return u"%s" % self.value

    class Meta:
        verbose_name = "mesureMonth"
        ordering = ['-timestamp', 'server', 'probe']
