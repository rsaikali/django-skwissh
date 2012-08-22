# -*- coding: utf-8 -*-
import os
import tempfile
from logging.handlers import WatchedFileHandler
try:
    from django.conf import settings
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
    Patches default project settings LOGIN_URL.
    Don't know if it's the best way to do it... but it works...
    """
    settings.LOGIN_URL = "/skwissh/login"

    logger = logging.getLogger('skwissh')
    logger.setLevel(logging.DEBUG)
    log_filename = os.path.join(tempfile.gettempdir(), "cron.log")
    log_handler = WatchedFileHandler(filename=log_filename)
    formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)s %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
