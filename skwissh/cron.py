# -*- coding: utf-8 -*-
from django.utils.timezone import utc
from fabric.context_managers import hide
from fabric.decorators import task
from fabric.operations import run, sudo, local
from fabric.state import env
from fabric.tasks import execute
from skwissh.models import Server, Measure, MeasureDay, MeasureWeek, \
    MeasureMonth
from skwissh.settings import DAY_AVERAGE_PERIOD, WEEK_AVERAGE_PERIOD, \
    MONTH_AVERAGE_PERIOD
import datetime
import kronos
import logging
import threading

logger = logging.getLogger('skwissh')


###############################################################################
# GET MEASURES
###############################################################################
@kronos.register('*/1 * * * *')
def getMeasures():
    with hide('everything'):
        timestamp = datetime.datetime.utcnow().replace(tzinfo=utc)
        now = timestamp - datetime.timedelta(seconds=timestamp.second, microseconds=timestamp.microsecond)
        env.skip_bad_hosts = True
        env.parallel = False
        env.timeout = 2
        env.connection_attempts = 1
        servers = Server.objects.filter(is_measuring=False).select_related()
        for server in servers:
            try:
                server.is_measuring = True
                server.save(force_update=True)
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
                    for probe in probes:
                        if probe.graph_type.name in ['pie', 'text']:
                            Measure.objects.filter(server=server, probe=probe).delete()
                        Measure.objects.create(timestamp=now, server=server, probe=probe, value=outputs[probe.id])
                    server.state = outputs[-1]
            except Exception, e:
                logger.exception(e)
            finally:
                server.is_measuring = False
                server.save(force_update=True)
        logger.info("getMeasures duration : " + str(datetime.datetime.utcnow().replace(tzinfo=utc) - timestamp))
    return 0


@task
def launch_command(probes):
    outputs = {}

    if env.host_string == "127.0.0.1":
        server_up = True
    else:
        try:
            server_up = run("echo", shell=False, pty=False).succeeded
        except:
            server_up = False

    for probe in probes:
        if server_up:
            logger.debug("---> Sensor '%s'" % probe.display_name.encode('utf-8'))
            try:
                if env.host_string == "127.0.0.1":
                    output = local(probe.ssh_command, capture=True)
                elif probe.use_sudo:
                    output = sudo(probe.ssh_command, shell=False, pty=False)
                else:
                    output = run(probe.ssh_command, shell=False, pty=False)
                for python_command in probe.python_parse.splitlines():
                    exec(python_command)
            except Exception, e:
                logger.exception(e)
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
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    measures = Measure.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(minutes=period))

    if len(measures) == 0:
        logger.debug("Not enough data for last %d minutes : %s / %s" % (period, server.hostname, probe.display_name))
    else:
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
            thread = threading.Thread(target=calculateAveragesForPeriod, args=[period, classname, server, probe], name="SkwisshAverage.%s.%s" % (classname.__name__, probe.display_name.encode('utf-8').replace(" ", "_")))
            thread.setDaemon(False)
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()


@kronos.register('*/%s * * * *' % DAY_AVERAGE_PERIOD)
def averageDay():
    logger.info("Calculating average values for day / averaging each %d minutes" % DAY_AVERAGE_PERIOD)
    calculateAverage(DAY_AVERAGE_PERIOD, MeasureDay)
    daily_period = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(days=1)
    old_measures = MeasureDay.objects.filter(timestamp__lt=daily_period)
    logger.info("Deleting %d daily measures (before %s)..." % (len(old_measures), daily_period))
    old_measures.delete()


@kronos.register('*/%s * * * *' % WEEK_AVERAGE_PERIOD)
def averageWeek():
    logger.info("Calculating average values for week / averaging each %d minutes" % WEEK_AVERAGE_PERIOD)
    calculateAverage(WEEK_AVERAGE_PERIOD, MeasureWeek)
    weekly_period = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(days=7)
    old_measures = MeasureWeek.objects.filter(timestamp__lt=weekly_period)
    logger.info("Deleting %d weekly measures (before %s)..." % (len(old_measures), weekly_period))
    old_measures.delete()


@kronos.register('*/%s * * * *' % MONTH_AVERAGE_PERIOD)
def averageMonth():
    logger.info("Calculating average values for month / averaging each %d minutes" % MONTH_AVERAGE_PERIOD)
    calculateAverage(MONTH_AVERAGE_PERIOD, MeasureMonth)
    monthly_period = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(days=31)
    old_measures = MeasureMonth.objects.filter(timestamp__lt=monthly_period)
    logger.info("Deleting %d monthly measures (before %s)..." % (len(old_measures), monthly_period))
    old_measures.delete()
    max_period = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(minutes=MONTH_AVERAGE_PERIOD)
    old_measures = Measure.objects.filter(timestamp__lt=max_period)
    logger.info("Deleting %d single measures (before %s)..." % (len(old_measures), max_period))
    old_measures.delete()
