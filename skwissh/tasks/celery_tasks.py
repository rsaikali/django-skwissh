# -*- coding: utf-8 -*-
import tasks
from inspect import getmembers, isfunction
import sys
from celery.task import task

thismodule = sys.modules[__name__]

try:
    from djcelery.models import CrontabSchedule
    from djcelery.models import PeriodicTask
    from celery import schedules
except:
    pass

thismodule = sys.modules[__name__]

celery_tasks = []

for name, member in getmembers(tasks):
    if isfunction(member) and hasattr(member, "crontab"):
        celery_task = task(member)
        celery_task.crontab = member.crontab
        celery_tasks.append(celery_task)
        setattr(thismodule, name, celery_task)

def get_schedule(crontab):
    """Get djcelery CrontabSchedule object

    TODO: make real crontab validation
    """
    crontab_parts = crontab.split(" ")
    schedule_dict = {
        "minute": "*",
        "hour": "*",
        "day_of_week": "*",
        "day_of_month": "*",
        "month_of_year": "*",
    }
    if len(crontab_parts)==5:
        schedule_dict["minute"] = crontab_parts[0]
        schedule_dict["hour"] = crontab_parts[1]
        schedule_dict["day_of_week"] = crontab_parts[2]
        schedule_dict["day_of_month"] = crontab_parts[3]
        schedule_dict["month_of_year"] = crontab_parts[4]

    new_schedule = CrontabSchedule.from_schedule(schedules.crontab(**schedule_dict))
    new_schedule.save()
    return new_schedule

def install():
    uninstall()
    for task in celery_tasks:
        task_name = task.name
        print task_name
        PeriodicTask.objects.create(
            name = task.__name__,
            task=task_name,
            crontab=get_schedule(task.crontab)
        )

def uninstall():
    PeriodicTask.objects.filter(task__startswith="skwissh").delete()
