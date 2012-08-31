# -*- coding: utf-8 -*-
from django.utils.timezone import utc
from fabric.context_managers import hide, settings
from fabric.decorators import task
from fabric.operations import run, sudo, local
from fabric.state import env
from fabric.tasks import execute
from skwissh.models import Server, Measure, MeasureDay, MeasureWeek, \
    MeasureMonth, CronLog
from skwissh.settings import DAY_AVERAGE_PERIOD, WEEK_AVERAGE_PERIOD, \
    MONTH_AVERAGE_PERIOD
import datetime
import kronos
import logging
import thread
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
        env.timeout = 5
        env.connection_attempts = 1
        servers = Server.objects.filter(is_measuring=False).select_related()
        for server in servers:
            try:
                env.hosts = [server.ip]
                env.user = server.username
                env.password = server.password
                with hide('running', 'stdout', 'stderr', 'user'):
                    execute(launch_command, server, now)
            except Exception, e:
                logger.exception(e)
        logger.info("--- duration : " + str(datetime.datetime.utcnow().replace(tzinfo=utc) - timestamp))
    return 0


@task
def launch_command(server, timestamp):

    server.is_measuring = True
    server.save(force_update=True)

    if env.host_string == "127.0.0.1":
        server_up = True
    else:
        with settings(warn_only=True):
            server_up = run("test 1", shell=False, pty=False).succeeded

    for probe in server.probes.all():
        storeValue(server, probe, timestamp, server_up)

    server.state = server_up
    server.is_measuring = False
    server.save(force_update=True)


def storeValue(server, probe, timestamp, server_up):

    start = datetime.datetime.utcnow().replace(tzinfo=utc)
    success = False
    if server_up:
        try:
            with settings(warn_only=True):
                if env.host_string == "127.0.0.1":
                    output = local(probe.ssh_command, capture=True)
                elif probe.use_sudo:
                    output = sudo(probe.ssh_command, shell=False, pty=False)
                else:
                    output = run(probe.ssh_command, shell=False, pty=False)
            success = output.succeeded
            if not success:
                if probe.graph_type.name == 'text':
                    output = "No data"
                else:
                    output = "0"
            else:
                for python_command in probe.python_parse.splitlines():
                    exec(python_command)
        except Exception, e:
            logger.exception(e)
            success = False
            if probe.graph_type.name == 'text':
                output = "No data"
            else:
                output = "0"
    else:
        if probe.graph_type.name == 'text':
            output = "No data"
        else:
            output = "0"

    total_time = datetime.datetime.utcnow().replace(tzinfo=utc) - start
    duration = (total_time.seconds * 1000000) + total_time.microseconds
    try:
        if probe.graph_type.name == 'text':
            Measure.objects.filter(server=server, probe=probe).delete()
        measure = Measure.objects.create(timestamp=timestamp, server=server, probe=probe, value=str(output))
        CronLog.objects.create(timestamp=timestamp, server=server, probe=probe, measure=measure, success=success, duration=duration)
    except Exception, e:
        logger.exception(e)


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
        for probe in server.probes.all().filter(graph_type__name__in=['linegraph', 'bargraph']):
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
