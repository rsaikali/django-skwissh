# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from skwissh.fields import EncryptedCharField
import datetime


class GraphType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u"Nom"), null=True, blank=True)
    options = models.TextField(verbose_name=_(u"Options jqPlot"), null=True, blank=True)
    date_created = models.DateTimeField(verbose_name=_(u"Date de création"), null=True, auto_now_add=True, default=datetime.datetime.now())
    date_modified = models.DateTimeField(verbose_name=_(u"Date de modification"), null=True, auto_now=True, default=datetime.datetime.now())

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _(u"type de graphique")
        verbose_name_plural = _(u"types de graphiques")
        ordering = ['name']


def get_default_graph_type():
    return GraphType.objects.get(name="linegraph")


class Probe(models.Model):
    display_name = models.CharField(max_length=255, verbose_name=_(u"Nom de la sonde"))
    addon_name = models.CharField(max_length=255, verbose_name=_(u"Infos complémentaires (version linux...)"), null=True, blank=True)
    ssh_command = models.TextField(verbose_name=_(u"Commande SSH"))
    use_sudo = models.BooleanField(verbose_name=_(u"Utilise 'sudo' ?"), default=False)
    python_parse = models.TextField(verbose_name=_(u"Commande Python de parsing"), null=True, blank=True, default="output = output")
    graph_type = models.ForeignKey(GraphType, verbose_name=_(u"Type de graphique par défaut"), default=get_default_graph_type)
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
        verbose_name = _(u"sonde")
        ordering = ['display_name', 'addon_name']


class Server(models.Model):
    hostname = models.CharField(max_length=255, verbose_name=_(u"Nom du serveur"))
    ip = models.CharField(max_length=255, verbose_name=_(u"Adresse IP"), blank=True)
    state = models.BooleanField(verbose_name=_(u"Serveur accessible ?"), default=False)
    is_measuring = models.BooleanField(verbose_name=_(u"Serveur en cours de mesures ?"), default=False)
    username = models.CharField(max_length=50, verbose_name=_(u"Nom d'utilisateur SSH"), blank=True, default="")
    password = EncryptedCharField(max_length=50, verbose_name=_(u"Mot de passe SSH"), blank=True, default="")
    date_created = models.DateTimeField(verbose_name=_(u"Date de création"), null=True, auto_now_add=True, default=datetime.datetime.now())
    date_modified = models.DateTimeField(verbose_name=_(u"Date de modification"), null=True, auto_now=True, default=datetime.datetime.now())
    probes = models.ManyToManyField(Probe, verbose_name=_(u"Sondes"), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.hostname

    @models.permalink
    def get_absolute_url(self):
        return ('server-detail', [self.id])

    class Meta:
        verbose_name = _(u"serveur")
        ordering = ['hostname', 'ip']


class ServerGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u"Nom du groupe"))
    date_created = models.DateTimeField(verbose_name=_(u"Date de création"), null=True, auto_now_add=True, default=datetime.datetime.now())
    date_modified = models.DateTimeField(verbose_name=_(u"Date de modification"), null=True, auto_now=True, default=datetime.datetime.now())
    servers = models.ManyToManyField(Server, verbose_name=_(u"Serveurs"), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _(u"groupe de serveurs")
        verbose_name_plural = _(u"groupes de serveurs")
        ordering = ['name']


class Measure(models.Model):
    timestamp = models.DateTimeField(verbose_name=_(u"Date et heure"))
    server = models.ForeignKey(Server, verbose_name=_(u"Serveur"))
    probe = models.ForeignKey(Probe, verbose_name=_(u"Sonde"))
    value = models.CharField(max_length=4096, verbose_name=_(u"Valeur mesurée"))

    def __unicode__(self):
        return u"%s %s %s" % (self.timestamp, self.server.hostname, self.probe.display_name)

    class Meta:
        verbose_name = _(u"mesure")
        verbose_name_plural = _(u"mesures")
        ordering = ['-timestamp', 'server', 'probe']


class MeasureDay(models.Model):
    timestamp = models.DateTimeField(verbose_name=_(u"Date et heure"))
    server = models.ForeignKey(Server, verbose_name=_(u"Serveur"))
    probe = models.ForeignKey(Probe, verbose_name=_(u"Sonde"))
    value = models.CharField(max_length=4096, verbose_name=_(u"Valeur mesurée"))

    def __unicode__(self):
        return u"%s" % self.value

    class Meta:
        verbose_name = _(u"mesure (vue journalière)")
        verbose_name_plural = _(u"mesures (vue journalière)")
        ordering = ['-timestamp', 'server', 'probe']


class MeasureWeek(models.Model):
    timestamp = models.DateTimeField(verbose_name=_(u"Date et heure"))
    server = models.ForeignKey(Server, verbose_name=_(u"Serveur"))
    probe = models.ForeignKey(Probe, verbose_name=_(u"Sonde"))
    value = models.CharField(max_length=4096, verbose_name=_(u"Valeur mesurée"))

    def __unicode__(self):
        return u"%s" % self.value

    class Meta:
        verbose_name = _(u"mesure (vue hebdomadaire)")
        verbose_name_plural = _(u"mesures (vue hebdomadaire)")
        ordering = ['-timestamp', 'server', 'probe']


class MeasureMonth(models.Model):
    timestamp = models.DateTimeField(verbose_name=_(u"Date et heure"))
    server = models.ForeignKey(Server, verbose_name=_(u"Serveur"))
    probe = models.ForeignKey(Probe, verbose_name=_(u"Sonde"))
    value = models.CharField(max_length=4096, verbose_name=_(u"Valeur mesurée"))

    def __unicode__(self):
        return u"%s" % self.value

    class Meta:
        verbose_name = _(u"mesure (vue mensuelle)")
        verbose_name_plural = _(u"mesures (vue mensuelle)")
        ordering = ['-timestamp', 'server', 'probe']


class CronLog(models.Model):
    timestamp = models.DateTimeField(verbose_name=_(u"Date et heure"))
    action = models.CharField(max_length=50, verbose_name=_(u"Serveur"), blank=True)
    server = models.ForeignKey(Server, verbose_name=_(u"Serveur"), null=True)
    success = models.BooleanField(verbose_name=_(u"Succès de l'exécution ?"), default=False)
    message = models.TextField(verbose_name=_(u"Message"), null=True, default="")
    duration = models.FloatField(verbose_name=_(u"Durée en secondes"), default=0)

    def __unicode__(self):
        return u"%s %s %s %s" % (self.timestamp, self.server.hostname, self.success, self.duration)

    class Meta:
        verbose_name = _(u"exécution de tâches cron")
        verbose_name_plural = _(u"exécutions de tâches cron")
        ordering = ['-timestamp', '-server', '-action', ]
