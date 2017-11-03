
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
#                AGILE DBus Constants                   #
#                                                       #
#    Description: Constant variables of the AGILE       #
#       DBus Protocol API.                              #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.1                                       #
#    Date: November 2016                                #
#########################################################


# --- Variables ---------
BUS_NAME = "iot.agile.Protocol"
OBJ_PATH = "/iot/agile/Protocol"
SOCKET0 = "socket0"
SOCKET1 = "socket1"
try:
   import RPi.GPIO as GPIO
   if GPIO.RPI_INFO["TYPE"] == "Pi 3 Model B":
      SOCKET0DEV = "/dev/ttyUSB0"
      SOCKET1DEV = "/dev/ttyUSB0"
   else:
      SOCKET0DEV = "/dev/ttyUSB0"
      SOCKET1DEV = "/dev/ttyUSB0"
except:
   SOCKET0DEV = "/dev/ttyUSB0"
   SOCKET1DEV = "/dev/ttyUSB1"
SOCKETDEV = {SOCKET0: SOCKET0DEV, SOCKET1: SOCKET1DEV} 
# -----------------------
