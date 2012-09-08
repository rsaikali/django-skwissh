# -*- coding: utf-8 -*-
from django.utils.timezone import utc
from fabric.context_managers import hide, settings
from fabric.decorators import task, serial
from fabric.operations import run, sudo, local
from fabric.state import env
from fabric.tasks import execute
from skwissh.models import Server, Measure, MeasureDay, MeasureWeek, \
    MeasureMonth, CronLog
import datetime
import kronos
import thread
import threading
import traceback


###############################################################################
# GET MEASURES
###############################################################################
@kronos.register('*/1 * * * *')
def getMeasures():
    try:
        timestamp = datetime.datetime.utcnow().replace(tzinfo=utc)
        now = timestamp - datetime.timedelta(seconds=timestamp.second, microseconds=timestamp.microsecond)
        env.skip_bad_hosts = True
        env.timeout = 10
        env.connection_attempts = 1
        servers = Server.objects.filter(is_measuring=False)
        if servers:
            env.hosts = ["%s@%s" % (server.username, server.ip) for server in servers]
            env.passwords = dict([("%s@%s" % (server.username, server.ip), server.password) for server in servers])
            with hide('everything'):
                execute(launch_command, now)
    except:
        total_time = datetime.datetime.utcnow().replace(tzinfo=utc) - timestamp
        duration = float(int((total_time.seconds * 1000000) + total_time.microseconds) / 1000000.0)
        CronLog.objects.create(timestamp=timestamp, action="sensors", server=None, success=False, duration=duration, message=traceback.format_exc())
    return 0


@task
@serial
def launch_command(timestamp):
    try:
        start = datetime.datetime.utcnow().replace(tzinfo=utc)
        messages = []
        success = False
        server_up = False
        current_ip = str(env.host_string).split('@')[-1]
        server = Server.objects.get(ip=current_ip)
        server.is_measuring = True
        server.save(force_update=True)

        if server.ip in ["127.0.0.1", "localhost"]:
            server_up = True
        else:
            with settings(warn_only=True):
                server_up = run("test 1", shell=False, pty=False).succeeded

        if server_up:
            success = server_up
            messages.append("Server '%s' is up." % server.hostname)
            messages.append("-" * 40)
            probes = server.probes.all()
            for probe in probes:
                sensor_success, sensor_messages = storeValue(server, probe, timestamp, server_up)
                messages += sensor_messages
                success = success and sensor_success
        else:
            messages.append("Server '%s' is unreachable." % server.hostname)
            success = False
    except:
        messages.append(traceback.format_exc())
        success = False
    finally:
        server = Server.objects.get(ip=current_ip)
        server.state = server_up
        server.is_measuring = False
        server.save(force_update=True)
        total_time = datetime.datetime.utcnow().replace(tzinfo=utc) - start
        duration = float(int((total_time.seconds * 1000000) + total_time.microseconds) / 1000000.0)
        CronLog.objects.create(timestamp=timestamp, action="sensors", server=server, success=success, duration=duration, message="\n".join(messages))


def storeValue(server, probe, timestamp, server_up):
    try:
        messages = []
        current_ip = str(env.host_string).split('@')[-1]
        start = datetime.datetime.utcnow().replace(tzinfo=utc)

        messages.append("Executing sensor '%s'" % probe.display_name)

        with settings(warn_only=True):
            if current_ip in ["127.0.0.1", "localhost"]:
                output = local(probe.ssh_command, capture=True)
            elif probe.use_sudo:
                output = sudo(probe.ssh_command, shell=False, pty=False)
            else:
                output = run(probe.ssh_command, shell=False, pty=False)

        success = output.succeeded

        if not success:
            messages.append(output.stderr)
        try:
            for python_command in probe.python_parse.splitlines():
                exec(python_command)
        except:
            messages.append(traceback.format_exc())
            success = False

        if not success:
            output = "No data" if probe.graph_type.name == 'text' else "0"

        if probe.graph_type.name == 'text':
            Measure.objects.filter(server=server, probe=probe).delete()
            messages.append("\t-> Extracted value is %d characters long" % len(output))
        else:
            messages.append("\t-> Extracted values : %s" % output)
        Measure.objects.create(timestamp=timestamp, server=server, probe=probe, value=str(output))
    except:
        messages.append(traceback.format_exc())
        success = False
    finally:
        total_time = datetime.datetime.utcnow().replace(tzinfo=utc) - start
        duration = (total_time.seconds * 1000000) + total_time.microseconds
        messages.append("\t-> Sensor executed %s in %.2f seconds" % ("successfully" if success else "with errors", duration / 1000000.0))
        messages.append("-" * 40)
        return success, messages


###############################################################################
# AVERAGES CALCULATION
###############################################################################
DAY_AVERAGE_PERIOD = 10     # Day is displayed with 10 minutes average samples
WEEK_AVERAGE_PERIOD = 60   # Week is displayd with 1 hour average samples
MONTH_AVERAGE_PERIOD = 180  # Month is displayed with 3 hours average samples


def calculateAveragesForPeriod(period, classname, server, probe):
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    round_now = now - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)
    measures = Measure.objects.filter(server=server, probe=probe, timestamp__gte=now - datetime.timedelta(minutes=period))

    if len(measures) > 0:
        all_values = []
        for i in range(len(measures[0].value.split(";"))):
            values = [float(measure.value.split(";")[i]) for measure in measures]
            all_values.append(str(round(float(sum(values) / len(values)), 2)))
        classname.objects.create(timestamp=round_now, server=server, probe=probe, value=";".join(all_values))
    else:
        classname.objects.create(timestamp=round_now, server=server, probe=probe, value="0")


def calculateAverage(period, classname):
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    round_now = now - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)
    for server in Server.objects.all().select_related():
        try:
            threads = []
            for probe in server.probes.exclude(graph_type__name__in=['text']):
                thread = threading.Thread(target=calculateAveragesForPeriod, args=[period, classname, server, probe], name="SkwisshAverage.%s.%s" % (classname.__name__, probe.display_name.encode('utf-8').replace(" ", "_")))
                thread.setDaemon(False)
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            end = datetime.datetime.utcnow().replace(tzinfo=utc)
            total_time = end - now
            duration = float(int((total_time.seconds * 1000000) + total_time.microseconds) / 1000000.0)
            success = True
            message = "Calculated averages values for last %d minutes (server %s)" % (period, server.hostname)
        except:
            success = False
            message = traceback.format_exc()

        CronLog.objects.create(timestamp=round_now, action="average %dmin" % period, server=server, success=success, duration=duration, message=message)


@kronos.register('*/10 * * * *')
def averageDay():
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    round_now = now - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)

    calculateAverage(DAY_AVERAGE_PERIOD, MeasureDay)
    daily_period = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(days=1)
    old_measures = MeasureDay.objects.filter(timestamp__lt=daily_period)
    message = "Deleting %d averages values for last %d minutes created before %s" % (len(old_measures), DAY_AVERAGE_PERIOD, daily_period)
    old_measures.delete()

    end = datetime.datetime.utcnow().replace(tzinfo=utc)
    total_time = end - now
    duration = float(int((total_time.seconds * 1000000) + total_time.microseconds) / 1000000.0)
    CronLog.objects.create(timestamp=round_now, action="purge %dmin" % DAY_AVERAGE_PERIOD, server=None, success=True, duration=duration, message=message)


@kronos.register('0 */1 * * *')
def averageWeek():
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    round_now = now - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)

    calculateAverage(WEEK_AVERAGE_PERIOD, MeasureWeek)
    weekly_period = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(days=7)
    old_measures = MeasureWeek.objects.filter(timestamp__lt=weekly_period)
    message = "Deleting %d averages values for last %d minutes created before %s" % (len(old_measures), WEEK_AVERAGE_PERIOD, weekly_period)
    old_measures.delete()

    end = datetime.datetime.utcnow().replace(tzinfo=utc)
    total_time = end - now
    duration = float(int((total_time.seconds * 1000000) + total_time.microseconds) / 1000000.0)
    CronLog.objects.create(timestamp=round_now, action="purge %dmin" % WEEK_AVERAGE_PERIOD, server=None, success=True, duration=duration, message=message)


@kronos.register('0 */3 * * *')
def averageMonth():
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    round_now = now - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)

    calculateAverage(MONTH_AVERAGE_PERIOD, MeasureMonth)
    monthly_period = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(days=31)
    old_measures = MeasureMonth.objects.filter(timestamp__lt=monthly_period)
    message = "Deleting %d averages values for last %d minutes created before %s" % (len(old_measures), MONTH_AVERAGE_PERIOD, monthly_period)
    old_measures.delete()

    end = datetime.datetime.utcnow().replace(tzinfo=utc)
    total_time = end - now
    duration = float(int((total_time.seconds * 1000000) + total_time.microseconds) / 1000000.0)
    CronLog.objects.create(timestamp=round_now, action="purge %dmin" % MONTH_AVERAGE_PERIOD, server=None, success=True, duration=duration, message=message)

    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    round_now = now - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)

    max_period = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(minutes=MONTH_AVERAGE_PERIOD)
    old_measures = Measure.objects.filter(timestamp__lt=max_period)
    message = "Deleting %d sensors values created before %s" % (len(old_measures), max_period)
    old_measures.delete()
    old_logs = CronLog.objects.filter(timestamp__lt=max_period)
    old_logs.delete()

    end = datetime.datetime.utcnow().replace(tzinfo=utc)
    total_time = end - now
    duration = float(int((total_time.seconds * 1000000) + total_time.microseconds) / 1000000.0)
    CronLog.objects.create(timestamp=round_now, action="purge sensors", server=None, success=True, duration=duration, message=message)
