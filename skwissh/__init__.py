# -*- coding: utf-8 -*-
from skwissh.settings import patch_settings

###############################################################################
# Skwissh version
###############################################################################
VERSION = (0, 0, 8)  # PEP 386
__version__ = ".".join([str(x) for x in VERSION])

try:
    patch_settings()
except:
    pass
