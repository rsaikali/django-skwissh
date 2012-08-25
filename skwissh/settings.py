# -*- coding: utf-8 -*-
from logging.handlers import RotatingFileHandler
import os
import skwissh
import tempfile
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
    log_dir = os.path.join(tempfile.gettempdir(), "skwissh_%s_logs" % skwissh.__version__)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_filename = os.path.join(log_dir, "skwissh_%s_cron.log" % skwissh.__version__)
    log_handler = RotatingFileHandler(filename=log_filename, maxBytes=1024 * 100, backupCount=10)
    formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)s %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
