#!/usr/bin/env python3

############################################################################
# Copyright (c) 2016, 2017 Libelium Comunicaciones Distribuidas S.L.       #
#                                                                          #
# All rights reserved. This program and the accompanying materials         #
# are made available under the terms of the Eclipse Public License v1.0    #
# and Eclipse Distribution License v1.0 which accompany this distribution. #
#                                                                          #
# The Eclipse Public License is available at                               #
#    http://www.eclipse.org/legal/epl-v10.html                             #
# and the Eclipse Distribution License is available at                     #
#   http://www.eclipse.org/org/documents/edl-v10.php.                      #
#                                                                          #
# Contributors:                                                            #
#    David Palomares - Initial API and implementation                      #
############################################################################

#########################################################
#            AGILE DBus Protocol Server                 #
#                                                       #
#    Description: Runs the AGILE DBus Protocol defined  #
#       in the AGILE API for the XBee 802.15.4 and XBee #
#       ZigBee protocols.                               #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.2                                       #
#    Date: November 2016                                #
#########################################################

# --- Imports -----------
import sys
from gi.repository import GLib
import dbus
import dbus.service
import dbus.mainloop.glib
from dbus_protocols import dbus_protocol as dbP
##from dbus_protocols import dbus_xbee_802_15_4 as xb_802
from dbus_protocols import dbus_xbee_zigbee as xb_zb
##from dbus_protocols import dbus_lorawan as lorawan
from dbus_protocols import dbus_constants as db_cons
import logging
# -----------------------


# --- Variables ---------
LOGLEVEL = logging.INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL
mainloop = GLib.MainLoop()
# -----------------------


# --- Classes -----------
class DBusExit(dbus.service.Object):
    
   def __init__(self):
      super().__init__(dbus.SessionBus(), db_cons.OBJ_PATH) 
    
   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="")
   def Exit(self):
      mainloop.quit() 
# -----------------------


# --- Functions ---------
def dbusService():
   dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
   #dbe = DBusExit()
   ##xb1 = xb_802.XBee_802_15_4()
   xb2 = xb_zb.XBee_ZigBee()
   ##lw = lorawan.LoRaWAN()
   logger.info("Running DBus service.")
   try:
      mainloop.run()
   except KeyboardInterrupt:
      print()
      try:
         mainloop.quit()
      except dbus.exceptions.DBusException:
         pass
      endProgram(0)
   
def endProgram(status):
   logger.info("DBus service stopped.")
   sys.exit(status)
# -----------------------
   

# --- Main program ------
if __name__ == "__main__":
   # Start logging
   logging.basicConfig(
      filemode="a",
      format="%(asctime)s [%(levelname)s] %(message)s",
      datefmt="%Y-%m-%d %H:%M:%S",
      level=LOGLEVEL
   )
   logger = logging.getLogger(db_cons.BUS_NAME)
   # Start DBus
   dbusService()   
   endProgram(0)
# -----------------------

