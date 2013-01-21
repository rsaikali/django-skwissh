.. image:: http://rsaikali.github.com/django-skwissh/images/skwissh/skwissh-logo.png

**DEMO SITE** : Visit the `Skwissh demo <http://skwissh.com>`_ (username ``test`` / password ``test``) to see Skwissh in action.

**More info** : `Github Pages for Skwissh <http://rsaikali.github.com/django-skwissh/>`_

**Python Package Index** : `django-skwissh <http://pypi.python.org/pypi?:action=display&name=django-skwissh>`_

**Travis** : `Last build status <http://travis-ci.org/#!/rsaikali/django-skwissh>`_

.. image:: https://secure.travis-ci.org/rsaikali/django-skwissh.png?branch=master

**New Android application** : `Find Android Skwissh on Google Play <http://play.google.com/store/apps/details?id=com.saikali.android_skwissh>`_
  
.. image:: http://www.android.com/images/brand/android_app_on_play_logo_large.png


============
Introduction
============

A Django application for remotely monitoring servers using SSH.

In background (crontabed jobs) Skwissh uses `Python Fabric <http://fabfile.org>`_ to execute SSH commands, aka. "sensors", get the output and store timestamped values.
Measures are taken every minute.

On the other side, Skwissh is able to display nice charts (linechart, piechart or simple text) with aggregated measures. 

Default sensors available (tested on Ubuntu 12.04) :

* Memory
* CPU
* WaitIO
* Load Averages
* Disk usage
* Top

But you can easily add your own ones !!

Follow @skwissh on `Twitter <https://twitter.com/skwissh>`_ to see latest updates.

============
Installation
============

Skwissh can be installed from Pypi:

::

    pip install django-skwissh

Configure your Django project in a normal way (database, etc...).

Add ``skwissh`` and ``kronos`` to your Django ``INSTALLED_APPS``:

::

    INSTALLED_APPS = (
        ...
        'kronos',
        'skwissh',
    )

Add Skwissh to your ``urls.py``:

::

   # Skwissh
   url(r'^skwissh/', include('skwissh.urls')),

Synchronize your database (this command will load defaut sensors through fixtures):

::

   ./manage.py syncdb
    
Install Skwissh tasks (will write to your user crontab, thanks to 'django-kronos'):

::

   ./manage.py installsensors
    
You can check that 4 crontab job have been configured:

::

   crontab -l

If you want to activate i18n (French & English currently supported), follow the next steps:

In your project ``settings.py``, add the Django ``LocaleMiddleware`` and set the ``LANGUAGES`` variable:

::

   MIDDLEWARE_CLASSES = (
      ...
      'django.middleware.locale.LocaleMiddleware',
      ...
   )

   LANGUAGES = (
      ('fr', 'Français'),
      ('en', 'English'),
   )

You're ready to go ! 
Connect to the application and start configure your servers and sensors !


=====================
Changing task backend
=====================

By default ``kronos`` is used for running jobs. This behavior can be changed by using
different task backend. At the moment there are only two backends availible:

* ``kronos``
* ``celery``

Backend can be changed with ``SKWISSH_TASK_BACKEND`` in ``settings.py`` of your project.

Celery as task backend
~~~~~~~~~~~~~~~~~~~~~~

If you want to use `celery <http://celeryproject.org/>`_ as your task backend you must
install ``django-celery`` package:

::

    pip install django-celery

Add 'djcelery' to your Django ``INSTALLED_APPS``:

::

    INSTALLED_APPS = (
        ...
        'djcelery',
    )

And add following lines to ``setup.py``:

::

    # select celery backend
    SKWISSH_TASK_BACKEND = "celery"

    # tell celery where to look for tasks
    CELERY_IMPORTS = (
        "skwissh.tasks.celery_tasks",
    )

    # use DatabaseScheduler
    CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

You must also choose and configure celery backend. If you don't know how
please refer to `celery documentation <http://docs.celeryproject.org/en/latest/index.html>`_.

To start collecting data install tasks in database schedule:

::

    ./manage.py installsensors

And start celery worker with heartbeat enabled:
::

    ./manage.py celery worker -B

Or as two separate processes:

::

    ./manage.py celery beat
    ./manage.py celery worker

===========
Screenshots
===========

Load averages
~~~~~~~~~~~~~
.. image:: http://rsaikali.github.com/django-skwissh/images/skwissh/loads-screenshot.png

Disk usage
~~~~~~~~~~
.. image:: http://rsaikali.github.com/django-skwissh/images/skwissh/diskusage-screenshot.png

Top output
~~~~~~~~~~
.. image:: http://rsaikali.github.com/django-skwissh/images/skwissh/top-screenshot.png

Server edition
~~~~~~~~~~~~~~
.. image:: http://rsaikali.github.com/django-skwissh/images/skwissh/editserver-screenshot.png

Sensor edition
~~~~~~~~~~~~~~
.. image:: http://rsaikali.github.com/django-skwissh/images/skwissh/editsensor-screenshot.png

=======
Credits
=======

* Uses Django 1.4.1 (https://www.djangoproject.com).
* Uses Django applications and addons :

  - django-kronos (https://github.com/jgorset/django-kronos) from Johannes Gorset (https://github.com/jgorset).
  - django-extra-views (https://github.com/AndrewIngram/django-extra-views) from Andrew Ingram (https://github.com/AndrewIngram). 

* Uses Fabric (http://fabfile.org) SSH Python library.
* Uses jqPlot (http://www.jqplot.com) jQuery plotting and charting library.
* Uses Zurb Foundation (http://foundation.zurb.com) responsive CSS/JS/HTML bootstrap.
* Includes icons from TheNounProject (http://thenounproject.com).
