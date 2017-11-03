
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
#            AGILE DBus Protocol ProtocolTemplate       #
#                                                       #
#    Description: Class of the Protocol defined in the  #
#       in the AGILE API with the implementation of the #
#       ProtocolTemplate protocol.                      #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.1                                       #
#    Date: June 2016                                    #
#########################################################

# --- Imports -----------
import dbus
import dbus.service
from dbus_protocols import dbus_protocol as dbP
from dbus_protocols import dbus_constants as db_cons
import logging
# -----------------------


# --- Variables ---------
PROTOCOL_NAME = "ProtocolTemplate" #TODO: Search and replace
# -----------------------


# --- Classes -----------
class ProtocolTemplate(dbP.Protocol):
   
   def __init__(self):     
      super().__init__()
      self._protocol_name = PROTOCOL_NAME
      self._exception = ProtocolTemplate_Exception()
      self._objS0 = ProtocolTemplate_Obj(self._socket0)
      self._objS1 = ProtocolTemplate_Obj(self._socket1)
       

class ProtocolTemplate_Exception(dbP.ProtocolException):
   
   def __init__(self, msg=""):
      super().__init__(PROTOCOL_NAME, msg)
      
    
class ProtocolTemplate_Obj(dbP.ProtocolObj):

   def __init__(self, socket):
      super().__init__(PROTOCOL_NAME, socket)
      
   # Override DBus object methods
   #TODO
# -----------------------


