# -*- coding: utf-8 -*-
import tasks
from inspect import getmembers, isfunction
import sys
import kronos

thismodule = sys.modules[__name__]

for name, member in getmembers(tasks):
    if isfunction(member) and hasattr(member, "crontab"):
        setattr(thismodule, name, kronos.register(member.crontab)(member))

def install():
    kronos.reinstall()

def uninstall():
    kronos.uninstall()