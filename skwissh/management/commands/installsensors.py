# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from skwissh.tasks import celery_tasks, kronos_tasks

class Command(BaseCommand):
    help = 'Installs tasks either using django-kronos or django-celery'

    def handle(self, *args, **options):
        backend = getattr(settings, "SKWISSH_TASK_BACKEND", "kronos")

        if backend == "kronos":
            kronos_tasks.install()

        elif backend == "celery":
            celery_tasks.install()

        else:
            raise CommandError("imporperly configured!")