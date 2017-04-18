# -*- coding: utf-8 -*-
try:
    from django.core.urlresolvers import reverse
    from django.conf import settings
except:
    pass


###############################################################################
# Patch Django project settings
###############################################################################
def patch_settings():
    """
    Patches default project settings LOGIN_URL.
    Don't know if it's the best way to do it... but it works...
    """
    settings.LOGIN_URL = reverse("skwissh.views.login_skwissh")
