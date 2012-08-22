# -*- coding: utf-8 -*-
from fabric.context_managers import hide
from fabric.decorators import task, parallel
from fabric.operations import run, sudo
from fabric.state import env
from fabric.tasks import execute
from skwissh.models import Server, Measure, MeasureDay, MeasureWeek, \
    MeasureMonth
from skwissh.settings import DAY_AVERAGE_PERIOD, WEEK_AVERAGE_PERIOD, \
    MONTH_AVERAGE_PERIOD
import datetime
import fabric
import kronos
import logging
import threading

logger = logging.getLogger('skwissh')


###############################################################################
# GET MEASURES
###############################################################################
@kronos.register('*/1 * * * *')
def getMeasures():
    timestamp = datetime.datetime.now()
    now = timestamp - datetime.timedelta(seconds=timestamp.second, microseconds=timestamp.microsecond)
    env.skip_bad_hosts = True
    env.parallel = True
    env.timeout = 2
    env.connection_attempts = 1
    try:
        for server in Server.objects.all().select_related():
            logger.info("Getting measures for server '%s'" % server.hostname.encode('utf-8'))
            probes = server.probes.all()
            if len(probes) == 0:
                continue
            env.hosts = [server.ip]
            env.user = server.username
            env.password = server.password
            with hide('running', 'stdout', 'stderr', 'user'):
                value = execute(launch_command, probes)
                outputs = value[server.ip]
                server.state = outputs[-1]
                server.save()
                for probe in probes:
                    if probe.graph_type.name in ['pie', 'text']:
                        Measure.objects.filter(server=server, probe=probe).delete()
                    Measure.objects.create(timestamp=now, server=server, probe=probe, value=outputs[probe.id])
    except Exception, e:
        logger.error(str(e))
    logger.info("GETTING MESURES DURATION : " + str(datetime.datetime.now() - timestamp))
    fabric.network.disconnect_all()
    return 0


@task
@parallel
def launch_command(probes):
    outputs = {}

    try:
        server_up = run("echo", shell=False, pty=False).succeeded
    except:
        server_up = False

    for probe in probes:
        if server_up:
            logger.debug("---> Sensor '%s'" % probe.display_name.encode('utf-8'))
            try:
                if probe.use_sudo:
                    output = sudo(probe.ssh_command, shell=False, pty=False)
                else:
                    output = run(probe.ssh_command, shell=False, pty=False)
                for python_command in probe.python_parse.splitlines():
                    exec(python_command)
            except:
                if probe.graph_type.name == 'linegraph':
                    output = 0
                elif probe.graph_type.name == 'pie':
                    output = "Inconnu;100"
                else:
                    output = "Aucune donnée"
        else:
            logger.debug("---> Sensor '%s' : server is unreachable..." % probe.display_name.encode('utf-8'))
            if probe.graph_type.name == 'linegraph':
                output = 0
            elif probe.graph_type.name == 'pie':
                output = "Inconnu;100"
            else:
                output = "Aucune donnée"
        outputs[probe.id] = output
    outputs[-1] = server_up
    return outputs


def calculateAveragesForPeriod(period, classname, server, probe):
    now = datetime.datetime.now()
    measures = Measure.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(minutes=period))
    all_values = []
    for i in range(len(measures[0].value.split(";"))):
        values = [float(measure.value.split(";")[i]) for measure in measures]
        all_values.append(str(round(float(sum(values) / len(values)), 2)))

    round_now = now - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)
    logger.debug("Average values for last %d minutes : %s / %s / %s" % (period, server.hostname, probe.display_name, ";".join(all_values)))
    classname.objects.create(timestamp=round_now, server=server, probe=probe, value=";".join(all_values))


def calculateAverage(period, classname):
    threads = []
    for server in Server.objects.all():
        for probe in server.probes.all().filter(graph_type__name='linegraph'):
            thread = threading.Thread(target=calculateAveragesForPeriod, args=[period, classname, server, probe])
            thread.setDaemon(False)
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()


@kronos.register('*/%s * * * *' % DAY_AVERAGE_PERIOD)
def averageDay():
    logger.info("Calculating average values for day / averaging each %d minutes" % DAY_AVERAGE_PERIOD)
    calculateAverage(DAY_AVERAGE_PERIOD, MeasureDay)
    old_measures = MeasureDay.objects.filter(timestamp__lt=datetime.datetime.now() - datetime.timedelta(days=1))
    logger.info("Deleting %d daily measures..." % len(old_measures))
    old_measures.delete()


@kronos.register('*/%s * * * *' % WEEK_AVERAGE_PERIOD)
def averageWeek():
    logger.info("Calculating average values for week / averaging each %d minutes" % WEEK_AVERAGE_PERIOD)
    calculateAverage(WEEK_AVERAGE_PERIOD, MeasureWeek)
    old_measures = MeasureWeek.objects.filter(timestamp__lt=datetime.datetime.now() - datetime.timedelta(days=7))
    logger.info("Deleting %d weekly measures..." % len(old_measures))
    old_measures.delete()


@kronos.register('*/%s * * * *' % MONTH_AVERAGE_PERIOD)
def averageMonth():
    logger.info("Calculating average values for month / averaging each %d minutes" % MONTH_AVERAGE_PERIOD)
    calculateAverage(MONTH_AVERAGE_PERIOD, MeasureMonth)
    old_measures = MeasureMonth.objects.filter(timestamp__lt=datetime.datetime.now() - datetime.timedelta(days=31))
    logger.info("Deleting %d monthly measures..." % len(old_measures))
    old_measures.delete()
    old_measures = Measure.objects.filter(timestamp__lt=datetime.datetime.now() - datetime.timedelta(minutes=MONTH_AVERAGE_PERIOD))
    logger.info("Deleting %d single measures..." % len(old_measures))
    old_measures.delete()
