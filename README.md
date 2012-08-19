#######
Skwissh
#######

A Django application for remotely monitoring servers using SSH.

In background (crontabed jobs) Skwissh uses `Python Fabric <http://fabfile.org>`_ to execute SSH commands, aka. "sensors", get the output and store timestamped values.

On the other side, Skwissh is able to display nice charts (linechart, piechart or simple text) with aggregated measures. 

Default sensors available (tested on Ubuntu 12.04) :

* Memory
* CPU
* WaitIO
* Load Averages
* Disk usage
* Top

But you can easily add your own ones !!

More information on `our website <http://skwissh.com>`_ (under construction...). 

***********
Screenshots
***********

![](http://github.com/rsaikali/django-skwissh/raw/master/doc/images/loads-screenshot.png)

![](http://github.com/rsaikali/django-skwissh/raw/master/doc/images/diskusage-screenshot.png)

![](http://github.com/rsaikali/django-skwissh/raw/master/doc/images/top-screenshot.png)

************
Installation
************

Configure a Django project (database, etc...)

Add ``skwissh`` and ``kronos`` to your Django ``INSTALLED_APPS`` ::

	INSTALLED_APPS = (
		...
		'kronos',
		'skwissh',
	)

Synchronize your database (this command will load defaut sensors through fixtures)::

    ./manage.py syncdb
    
Install Skwissh tasks (will write to your user crontab, thanks to 'django-kronos')::

    ./manage.py installtasks
    
Check that 4 crontab job have been configured::

	crontab -l

You're ready to go ! 
Connect to the application and start configure your servers !

*******
Credits
*******

* Uses `Django 1.4.1 <https://www.djangoproject.com/>`_.
* Uses Django applications and addons :

  * `django-kronos <https://github.com/jgorset/django-kronos>`_ from `Johannes Gorset <https://github.com/jgorset>`_.
  * `django-extra-views <https://github.com/AndrewIngram/django-extra-views>`_ from `Andrew Ingram <https://github.com/AndrewIngram>`_. 
* Uses `Fabric <http://fabfile.org/>`_ SSH Python library.
* Uses `jqPlot <http://www.jqplot.com/>`_ jQuery plotting and charting library.
* Uses `Zurb Foundation <http://foundation.zurb.com/>`_ responsive CSS/JS/HTML bootstrap.
* Includes icons from `TheNounProject <http://thenounproject.com/>`_.
