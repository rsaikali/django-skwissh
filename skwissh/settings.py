# -*- coding: utf-8 -*-
try:
    from django.conf import settings
    from logging.handlers import SysLogHandler
    from django.utils.translation import ugettext as _
    import logging
except:
    pass

###############################################################################
# AVERAGES CALCULATION SETTINGS
###############################################################################
# Should be less than 60 (or must change kronos decorator in cron.py, because crontab doesn't support */120 for minutes for example)...
DAY_AVERAGE_PERIOD = 5     # Day is displayed with 5 minutes average samples
WEEK_AVERAGE_PERIOD = 30   # Week is displayd with 30 minutes average samples
MONTH_AVERAGE_PERIOD = 60  # Month is displayed with 60 minutes average samples


###############################################################################
# Patch Django project settings
###############################################################################
def patch_settings():
    """
    Patches default project settings.
    Don't know if it's the best way to do it... but it works...
    I do that because I don't want to force users to manually edit lots of settings, except 'skissh' in INSTALLED_APPS.
    """
    settings.LOGIN_URL = "/skwissh/login"

    settings.LANGUAGES = (
        ('fr', _(u'Français')),
        ('en', _(u'Anglais')),
    )

    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'skwissh-cache'
        }
    }

    settings.MIDDLEWARE_CLASSES += (
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.gzip.GZipMiddleware',
        'django.middleware.http.ConditionalGetMiddleware',
    )

    logger = logging.getLogger('skwissh')
    logger.setLevel(logging.DEBUG)
    syslog = SysLogHandler(address='/dev/log')
    formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    syslog.setFormatter(formatter)
    logger.addHandler(syslog)
