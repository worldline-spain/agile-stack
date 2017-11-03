
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
#            AGILE DBus Protocol Base                   #
#                                                       #
#    Description: Base class of the Protocol defined    #
#       in the AGILE API with all the operations. Other #
#       classes can inherit and extend this class to    #
#       implmenet the different protocols.              #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.1                                       #
#    Date: June 2016                                    #
#########################################################

# --- Imports -----------
import dbus
import dbus.service
from dbus_protocols import dbus_constants as db_cons
import logging
# -----------------------


# --- Variables ---------

# -----------------------


# --- Classes -----------
class ProtocolException(dbus.DBusException):

   def __init__(self, protocol_name, msg=""):
      if msg == "":         
         super().__init__("Exception")
      else:
         super().__init__(msg)
      self._dbus_error_name = db_cons.BUS_NAME + "." + protocol_name
      
        
class ProtocolObj(dbus.service.Object):
   
   def __init__(self, protocol_name, socket):
      self._logger = logging.getLogger(db_cons.BUS_NAME)
      self._bus_name = db_cons.BUS_NAME
      self._obj_path = db_cons.OBJ_PATH
      self._socket = socket
      self._protocol_name = protocol_name   
      self._connected = False
      self._full_path = self._obj_path + "/" + protocol_name + "/" + socket
      super().__init__(dbus.SessionBus(), self._full_path)
      
   def _getConnected(self):
      return self._connected
      
   def _setConnected(self, status):
      if status:
         self._connected = True
      else:
         self._connected = False 
      
   def _getSocketDev(self, socket):
      return db_cons.SOCKETDEV[socket]
         
   # AGILE API Methods  
      
   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="b")
   def Connected(self):
      return _getConnected()

   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="s")
   def Driver(self):
      return "No driver."

   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="s")
   def Name(self):
      return self._protocol_name

   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="")
   def Connect(self):
      raise Protocol_Exception(self._protocol_name, "Function not supported.")

   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="")
   def Disconnect(self):
      raise Protocol_Exception(self._protocol_name, "Function not supported.")

   @dbus.service.method(db_cons.BUS_NAME, in_signature="a{sv}", out_signature="") 
   def Discover(self, args):
      raise Protocol_Exception(self._protocol_name, "Function not supported.")

   @dbus.service.method(db_cons.BUS_NAME, in_signature="sa{sv}", out_signature="")
   def Exec(self, op, args):
      raise Protocol_Exception(self._protocol_name, "Function not supported.")

   @dbus.service.method(db_cons.BUS_NAME, in_signature="a{sv}", out_signature="")
   def Setup(self, args):
      raise Protocol_Exception(self._protocol_name, "Function not supported.")

   @dbus.service.method(db_cons.BUS_NAME, in_signature="a{sv}", out_signature="")
   def Send(self, args):
      raise Protocol_Exception(self._protocol_name, "Function not supported.")

   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="a{sv}")
   def Receive(self):
      raise Protocol_Exception(self._protocol_name, "Function not supported.")

   @dbus.service.method(db_cons.BUS_NAME, in_signature="a{sv}", out_signature="")
   def Subscribe(self, args):
      raise Protocol_Exception(self._protocol_name, "Function not supported.")


class Protocol():

   def __init__(self):
      self._socket0 = db_cons.SOCKET0
      self._socket1 = db_cons.SOCKET1
      self._name = dbus.service.BusName(db_cons.BUS_NAME, dbus.SessionBus())
# -----------------------


