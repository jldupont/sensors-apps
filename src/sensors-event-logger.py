#!/usr/bin/env python
"""
    @author: Jean-Lou Dupont
"""
PROJECT_NAME="sensors-apps"
APP_NAME="event-logger"
POLL_TIMEOUT=250

import os
import sys
import gtk

## For development environment
ppkg=os.path.abspath( os.getcwd() + PROJECT_NAME)
if os.path.exists(ppkg):
    sys.path.insert(0, ppkg)

from system import *
Bus.publish(None, "%logpath", APP_NAME, "~/.%s/%s.log" % (PROJECT_NAME, APP_NAME))
#Bus.debug=True

import dbus.glib
import gobject              #@UnresolvedImport

gobject.threads_init()
dbus.glib.init_threads()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

## CUSTOMIZE {{     
from apps import app_event_logger
     
import sensors_apps.ctls.event_logger
## }} CUSTOMIZE 


def hQuit(*pa):
    gtk.main_quit()
Bus.subscribe("%quit", hQuit)

pcount=0
def idle():
    global pcount
    Bus.publish("__idle__", "%poll", pcount)
    pcount=pcount+1
    return True

gobject.timeout_add(POLL_TIMEOUT, idle)
gtk.main()
