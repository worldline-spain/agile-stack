
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
#            AGILE DBus Protocol LoRaWAN                #
#                                                       #
#    Description: Class of the Protocol defined in the  #
#       in the AGILE API with the implementation of the #
#       LoRaWAN protocol.                               #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.1                                       #
#    Date: November 2016                                #
#########################################################

# --- Imports -----------
import dbus
import dbus.service
from dbus_protocols import dbus_protocol as dbP
from dbus_protocols import dbus_constants as db_cons
import logging
import serial
import time
# -----------------------


# --- Variables ---------
# LoRaWAN Module
PROTOCOL_NAME = "LoRaWAN"
LORAWAN_MODE = "LoRaWAN"
LORA_MODE = "LoRa"
SETUP = {
   "BAUDRATE": "baudrate",
   "MODE": "mode"
}
DEF_BAUDRATE = 57600
TIMEOUT = 2
DEF_MODE = LORAWAN_MODE
CMD = {
   "SYS_RESET": b"sys reset\r\n",
   "MAC_SAVE": b"mac save\r\n",
   "MAC_PAUSE": b"mac pause\r\n",
   "MAC_RESUME": b"mac resume\r\n",
   "MAC_JOIN": "mac join", # + mode + \r\n
   "MAC_TX": "mac tx", # + type + port + data + \r\n
   "MAC_SET": "mac set", # + parameter + value + \r\n
   "RAD_RX": b"radio rx 0\r\n", # The rxWindowSize is in Continuous Reception
   "RAD_TX": "radio tx", # + data + \r\n
   "RAD_SET": "radio set" # + parameter + value + \r\n
}
RESPONSE = {
   "OK": b"ok\r\n", 
   "INVALID_PARAM": b"invalid_param\r\n", 
   "BUSY": b"busy\r\n",
   "DENIED": b"denied\r\n",
   "ACCEPTED": b"accepted\r\n", 
   "KEYS_NOT_INIT": b"keys_not_init\r\n",
   "NOT_JOINED": b"not_joined\r\n",
   "NO_FREE_CH": b"no_free_ch\r\n",
   "SILENT": b"silent\r\n",
   "FC_ERR": b"frame_counter_err_rejoin_needed\r\n",
   "MAC_PAUSED": b"mac_paused\r\n",
   "INVALID_DATA_LEN": b"invalid_data_len\r\n",
   "MAC_ERR":b"mac_err\r\n",
   "MAC_RX": b"mac_rx", # + port + data "\r\n"
   "MAC_TX": b"mac_tx_ok", 
   "RAD_ERR": b"radio_err\r\n", 
   "RAD_RX": b"radio_rx", # + data + "\r\n" 
   "RAD_TX": b"radio_tx_ok\r\n"
}
GUARDTIME = {
   "DEFAULT": 0.25,
   "SET": 0.25,
   "JOIN": 5.00,
   "PAUSE": 0.25,
   "SEND": 0.50,
   "RECEIVE": 0.50
}
# LoRaWAN Mode
SETLWOPTION = {
   "SAVE": "save",
   "JOIN": "join",
}
SETLWPARAM = {
   "DEVEUI": "deveui",
   "APPEUI": "appeui",
   "APPKEY": "appkey",
   "DEVADDR": "devaddr",
   "NWKSKEY": "nwkskey",
   "APPSKEY": "appskey"
}
JOINLWMODE = {
   "OTAA": "OTAA",
   "ABP": "ABP"
}
SENDLWPARAM = {
   "TYPE": "type",
   "PORT": "port",
   "DATA": "data"
}
SENDLWTYPE = {
   "CNF": "cnf",
   "UNCNF": "uncnf"
}
SENDLWPORT = {
   "MIN": 1,
   "MAX": 223
}
DEF_SAVE = False
DEF_JOIN = JOINLWMODE["OTAA"]
DEF_TYPE = "uncnf"
DEF_PORT = 3 
# LoRa Mode
MIN_LORA_TIME = 20000 # Minimum time needed to use LoRa mode in milliseconds
LORA_RX_TIMEOUT = 15 # Timeout of the RX (should match WDT) in seconds
SETRADPARAM = {
   "FREQ": "freq",
   "SF": "sf",
   "CR": "cr",
   "BW": "bw",
   "CRC": "crc",
   "PWR": "pwr",
   "WDT": "wdt" #XXX: Hardcoded
}
SENDRADPARAM = {
   "DATA": "data"
}
DEF_FREQ = "868100000"
DEF_SF = "sf12"
DEF_CR = "4/5"
DEF_BW = "125"
DEF_CRC = "on"
DEF_PWR = "13"
DEF_WDT = "15000"
# -----------------------


# --- Classes -----------
class LoRaWAN(dbP.Protocol):
   
   def __init__(self):     
      super().__init__()
      self._protocol_name = PROTOCOL_NAME
      self._exception = LoRaWAN_Exception()
      self._objS0 = LoRaWAN_Obj(self._socket0)
      self._objS1 = LoRaWAN_Obj(self._socket1)
       

class LoRaWAN_Exception(dbP.ProtocolException):
   
   def __init__(self, msg=""):
      super().__init__(PROTOCOL_NAME, msg)
      
    
class LoRaWAN_Obj(dbP.ProtocolObj):

   def __init__(self, socket):
      super().__init__(PROTOCOL_NAME, socket)
      self._setup = {
         SETUP["BAUDRATE"]: DEF_BAUDRATE,
         SETUP["MODE"]: DEF_MODE,
         SETLWOPTION["SAVE"]: DEF_SAVE,
         SETLWOPTION["JOIN"]: DEF_JOIN
      }
      
   # Override DBus object methods
   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="")
   def Connect(self):
      self._logger.debug("{}@Connect: Connect INIT".format(self._full_path))
      if self._getConnected():
         self._logger.debug("{}@Connect: Module is already connected".format(self._full_path))
         raise LoRaWAN_Exception("Module is already connected.")
      self._logger.debug("{}@Connect: Baudrate={}".format(self._full_path, self._setup[SETUP["BAUDRATE"]]))
      self._logger.debug("{}@Connect: Mode={}".format(self._full_path, self._setup[SETUP["MODE"]]))
      self._module = serial.Serial(self._getSocketDev(self._socket), self._setup[SETUP["BAUDRATE"]], timeout=TIMEOUT)     
      # Reset the module and clean the buffer
      self._module.write(CMD["SYS_RESET"])
      time.sleep(GUARDTIME["DEFAULT"])
      rx = self._module.readlines()
      # LoRa Mode
      if self._setup[SETUP["MODE"]] == LORA_MODE:
         # Parameters
         for key, value in self._setup.items():
            if key in SETRADPARAM.values():
               self._logger.debug("{}@Connect/LoRa: Setting {}={}".format(self._full_path, key, value))
               sendCmd = "{} {} {}\r\n".format(CMD["RAD_SET"], key, value).encode("utf-8")
               self._module.write(sendCmd)
               time.sleep(GUARDTIME["SET"])
               rx = self._module.readline()
               if not RESPONSE["OK"] in rx:
                  self._module.close()
                  self._logger.debug("{}@Connect/LoRa: Error setting {}={}".format(self._full_path, key, value))
                  raise LoRaWAN_Exception("Error setting the LoRa parameter \"{}\" with the value \"{}\".".format(key, value)) 
      # LoRaWAN Mode   
      else:
         # Parameters
         for key, value in self._setup.items():
            if key in SETLWPARAM.values():
               self._logger.debug("{}@Connect/LoRaWAN: Setting {}={}".format(self._full_path, key, value))
               sendCmd = "{} {} {}\r\n".format(CMD["MAC_SET"], key, value).encode("utf-8")
               self._module.write(sendCmd)
               time.sleep(GUARDTIME["SET"])
               rx = self._module.readline()
               if not RESPONSE["OK"] in rx:
                  self._module.close()
                  self._logger.debug("{}@Connect/LoRaWAN: Error setting {}={}".format(self._full_path, key, value)) 
                  raise LoRaWAN_Exception("Error setting the LoRaWAN parameter \"{}\" with the value \"{}\".".format(key, value)) 
         # Save parameters?
         if self._setup[SETLWOPTION["SAVE"]]:
            self._logger.debug("{}@Connect/LoRaWAN: Saving parameters".format(self._full_path))
            self._module.write(CMD["MAC_SAVE"])
            time.sleep(GUARDTIME["SET"])
            rx = self._module.readline()
            if not RESPONSE["OK"] in rx:
               self._module.close()
               self._logger.debug("{}@Connect/LoRaWAN: Error saving parameters".format(self._full_path))
               raise LoRaWAN_Exception("Error saving the LoRaWAN parameters.") 
         # Join mode
         self._logger.debug("{}@Connect/LoRaWAN: Joining in mode {}".format(self._full_path, self._setup[SETLWOPTION["JOIN"]]))
         sendCmd = "{} {}\r\n".format(CMD["MAC_JOIN"], self._setup[SETLWOPTION["JOIN"]]).encode("utf-8")
         self._module.write(sendCmd)
         time.sleep(GUARDTIME["SET"])
         rx = self._module.readline()
         if RESPONSE["OK"] in rx:
            time.sleep(GUARDTIME["JOIN"])
            rx = self._module.readline()
            if RESPONSE["ACCEPTED"] in rx:
               self._logger.debug("{}@Connect/LoRaWAN: Accepted".format(self._full_path))
            elif RESPONSE["DENIED"] in rx:
               self._logger.debug("{}@Connect/LoRaWAN: Denied".format(self._full_path))
               raise LoRaWAN_Exception("The module attempted to join the network but was rejected.")
            else:
               self._logger.debug("{}@Connect/LoRaWAN: Join OK but unknown error".format(self._full_path))
               raise LoRaWAN_Exception("Unknown error after joining to the network.")
         elif RESPONSE["INVALID_PARAM"] in rx:
            self._logger.debug("{}@Connect/LoRaWAN: Invalid param".format(self._full_path))
            raise LoRaWAN_Exception("Invalid parameter in the join command.")
         elif RESPONSE["KEYS_NOT_INIT"] in rx:
            self._logger.debug("{}@Connect/LoRaWAN: Keys not init".format(self._full_path))
            raise LoRaWAN_Exception("The keys corresponding to the join mode were not configured.")
         elif RESPONSE["NO_FREE_CH"] in rx:
            self._logger.debug("{}@Connect/LoRaWAN: No free channels".format(self._full_path))
            raise LoRaWAN_Exception("All channels are busy.")
         elif RESPONSE["SILENT"] in rx:
            self._logger.debug("{}@Connect/LoRaWAN: Silent".format(self._full_path))
            raise LoRaWAN_Exception("The module is in a Silent Immediately state.")
         elif RESPONSE["BUSY"] in rx:
            self._logger.debug("{}@Connect/LoRaWAN: Busy".format(self._full_path))
            raise LoRaWAN_Exception("The module is currently busy.")
         elif RESPONSE["MAC_PAUSED"] in rx:
            self._logger.debug("{}@Connect/LoRaWAN: Mac paused".format(self._full_path))
            raise LoRaWAN_Exception("The LoRaWAN mode is paused.")
         else:
            self._logger.debug("{}@Connect/LoRaWAN: Unknown error".format(self._full_path))
            raise LoRaWAN_Exception("Unknown error while joining to the network.")     
      self._setConnected(True)
      self._logger.debug("{}@Connect: Connect OK".format(self._full_path))

   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="")
   def Disconnect(self):
      self._logger.debug("{}@Disconnect: Disconnect INIT".format(self._full_path))
      if not self._getConnected():
         self._logger.debug("{}@Disconnect: Module is already disconnected".format(self._full_path))
         raise LoRaWAN_Exception("Module is already disconnected.")
      self._setConnected(False)
      self._module.close()
      self._logger.debug("{}@Disconnect: Disconnect OK".format(self._full_path)) 

   @dbus.service.method(db_cons.BUS_NAME, in_signature="a{sv}", out_signature="")
   def Setup(self, args):
      self._logger.debug("{}@Setup: Setup INIT".format(self._full_path))
      self._setup.clear()
      self._setup = {}
      # Store Setup Params: baudrate, mode, save
      baudrate = int(args.pop(SETUP["BAUDRATE"], DEF_BAUDRATE))
      if (baudrate < 0) or (baudrate > 921600):
         self._logger.debug("{}@Setup: Invalid baudrate".format(self._full_path))
         raise LoRaWAN_Exception("Invalid baudrate.")
      self._setup[SETUP["BAUDRATE"]] = baudrate
      mode = args.pop(SETUP["MODE"], DEF_MODE)
      if (mode != LORAWAN_MODE) and (mode != LORA_MODE):
         self._logger.debug("{}@Setup: Invalid baudrate".format(self._full_path))
         raise LoRaWAN_Exception("Invalid mode.")
      self._setup[SETUP["MODE"]] = mode
      # LoRa Mode
      if self._setup[SETUP["MODE"]] == LORA_MODE:
         # Store LoRa Params: freq, sf, cr, bw, crc, pwr
         self._setup[SETRADPARAM["FREQ"]] = args.pop(SETRADPARAM["FREQ"], DEF_FREQ)
         self._setup[SETRADPARAM["SF"]] = args.pop(SETRADPARAM["SF"], DEF_SF)
         self._setup[SETRADPARAM["CR"]] = args.pop(SETRADPARAM["CR"], DEF_CR)
         self._setup[SETRADPARAM["BW"]] = args.pop(SETRADPARAM["BW"], DEF_BW)
         self._setup[SETRADPARAM["CRC"]] = args.pop(SETRADPARAM["CRC"], DEF_CRC)
         self._setup[SETRADPARAM["PWR"]] = args.pop(SETRADPARAM["PWR"], DEF_PWR)
         self._setup[SETRADPARAM["WDT"]] = DEF_WDT #XXX: Hardcoded
      # LoRaWAN Mode
      else:
         # Store LoRaWAN Params: save, join, deveui, appeui, appkey, devaddr, nwkskey, appskey
         self._setup[SETLWOPTION["SAVE"]] = args.pop(SETLWOPTION["SAVE"], DEF_SAVE)
         join = args.pop(SETLWOPTION["JOIN"], DEF_JOIN)
         if not join in JOINLWMODE.values():
            self._logger.debug("{}@Setup: Invalid join".format(self._full_path))
            raise LoRaWAN_Exception("Invalid join.")
         self._setup[SETLWOPTION["JOIN"]] = join
         # As the rest of the parameters are optional, ask forgiveness not permission
         for lwParam in SETLWPARAM.values():
            try:
               self._setup[lwParam] = args.pop(lwParam)
            except KeyError:
               pass
      self._logger.debug("{}@Setup: Parameters={}".format(self._full_path, self._setup))
      self._logger.debug("{}@Setup: Setup OK".format(self._full_path, self._setup))
         
         
   @dbus.service.method(db_cons.BUS_NAME, in_signature="a{sv}", out_signature="")
   def Send(self, args):
      self._logger.debug("{}@Send: Send INIT".format(self._full_path))
      if not self._getConnected():
         self._logger.debug("{}@Send: Module is not connected".format(self._full_path))
         raise LoRaWAN_Exception("Module is not connected.")
      # LoRa mode
      if self._setup[SETUP["MODE"]] == LORA_MODE:
         # Pause LoRaWAN mode
         self._module.write(CMD["MAC_PAUSE"])
         time.sleep(GUARDTIME["PAUSE"])
         rx = self._module.readline()
         try:
            if int(rx) > MIN_LORA_TIME:
               # Send the message
               sendData = args.pop(SENDRADPARAM["DATA"], "")
               if not sendData:
                  self._logger.debug("{}@Send/LoRa: No data provided".format(self._full_path))
                  raise LoRaWAN_Exception("You must provide the data.")
               try:
                  int(sendData, 16)
               except ValueError:
                  self._logger.debug("{}@Send/LoRa: Invalid data format".format(self._full_path))
                  raise LoRaWAN_Exception("Invalid data format.")
               self._logger.debug("{}@Send/LoRaWAN: Send={{\'data\': \'{}\'}}".format(self._full_path, sendData))
               sendCmd = "{} {}\r\n".format(CMD["RAD_TX"], sendData).encode("utf-8")
               self._module.write(sendCmd)
               time.sleep(GUARDTIME["SET"])
               rx = self._module.readline()
               if RESPONSE["OK"] in rx:
                  time.sleep(GUARDTIME["SEND"])
                  rx = self._module.readline()
                  if RESPONSE["RAD_TX"] in rx:
                     # Transmission OK
                     self._logger.debug("{}@Send/LoRa: Send OK".format(self._full_path))
                  elif RESPONSE["RAD_ERR"] in rx:
                     self._logger.debug("{}@Send/LoRa: Transmission not successful".format(self._full_path))
                     raise LoRaWAN_Exception("The transmission was not successful.")
                  else:
                     self._logger.debug("{}@Send/LoRa: Sent but unknown error".format(self._full_path))
                     raise LoRaWAN_Exception("Unknown error after transmitting the data.")
               elif RESPONSE["BUSY"] in rx:
                  self._logger.debug("{}@Send/LoRa: Busy".format(self._full_path))
                  raise LoRaWAN_Exception("The module is currently busy.")
               elif RESPONSE["INVALID_PARAM"] in rx:
                  self._logger.debug("{}@Send/LoRa: Invalid param".format(self._full_path))
                  raise LoRaWAN_Exception("Invalid parameter in the radio tx command.")
               else:
                  self._logger.debug("{}@Send/LoRa: Unknown error".format(self._full_path))
                  raise LoRaWAN_Exception("Unknown error while transmitting the data.")
         except ValueError:
            self._logger.debug("{}@Send/LoRa: Could not pause the module to use LoRa mode".format(self._full_path))
            raise LoRaWAN_Exception("Could not pause the module to use LoRa mode.")
         # Restore LoRaWAN mode 
         finally:
            self._module.write(CMD["MAC_RESUME"])
            time.sleep(GUARDTIME["SET"])
            rx = self._module.readline()
      # LoRaWAN mode
      else:
         sendType = args.pop(SENDLWPARAM["TYPE"], DEF_TYPE)
         if not sendType in SENDLWTYPE.values():
            sendType = DEF_TYPE
         sendPort = args.pop(SENDLWPARAM["PORT"], DEF_PORT)
         if (sendPort < SENDLWPORT["MIN"]) or (sendPort > SENDLWPORT["MAX"]):
            sendPort = DEF_PORT
         sendData = args.pop(SENDLWPARAM["DATA"], "")
         if not sendData:
            self._logger.debug("{}@Send/LoRaWAN: No data provided".format(self._full_path))
            raise LoRaWAN_Exception("You must provide the data.")
         try:
            int(sendData, 16)
         except ValueError:
            self._logger.debug("{}@Send/LoRaWAN: Invalid data format".format(self._full_path))
            raise LoRaWAN_Exception("Invalid data format.")
         self._logger.debug("{}@Send/LoRaWAN: Send={{\'type\': \'{}\', \'port\': {}, \'data\': \'{}\'}}".format(self._full_path, sendType, sendPort, sendData))
         sendCmd = "{} {} {} {}\r\n".format(CMD["MAC_TX"], sendType, sendPort, sendData).encode("utf-8")
         self._module.write(sendCmd)
         time.sleep(GUARDTIME["SET"])
         rx = self._module.readline()
         if RESPONSE["OK"] in rx:
            time.sleep(GUARDTIME["SEND"])
            rx = self._module.readline()
            if RESPONSE["MAC_TX"] in rx:
               # Transmission OK, no ACK
               self._logger.debug("{}@Send/LoRaWAN: Send OK (no ACK)".format(self._full_path))
            elif RESPONSE["MAC_RX"] in rx: #FIXME: Clean serial buffer, wait for MAC_TX
               # Transmission OK, ACK received
               self._logger.debug("{}@Send/LoRaWAN: Send OK (ACK)".format(self._full_path))
            elif RESPONSE["MAC_ERR"] in rx:
               self._logger.debug("{}@Send/LoRaWAN: Transmission not successful".format(self._full_path))
               raise LoRaWAN_Exception("The transmission was not successful.")
            elif RESPONSE["INVALID_DATA_LEN"] in rx:
               self._logger.debug("{}@Send/LoRaWAN: Sent but invalid data length".format(self._full_path))
               raise LoRaWAN_Exception("The payload length is greater than the maximum in the current data rate.")
            else:
               raise LoRaWAN_Exception("Unknown error after transmitting the data.")
         elif RESPONSE["BUSY"] in rx:
            self._logger.debug("{}@Send/LoRaWAN: Busy".format(self._full_path))
            raise LoRaWAN_Exception("The module is currently busy.")
         elif RESPONSE["INVALID_PARAM"] in rx:
            self._logger.debug("{}@Send/LoRaWAN: Invalid param".format(self._full_path))
            raise LoRaWAN_Exception("Invalid parameter in the mac tx command.")
         elif RESPONSE["NOT_JOINED"] in rx:
            self._logger.debug("{}@Send/LoRaWAN: Not joined".format(self._full_path))
            raise LoRaWAN_Exception("The module is not joined to the network.")
         elif RESPONSE["NO_FREE_CH"] in rx:
            self._logger.debug("{}@Send/LoRaWAN: No free channels".format(self._full_path))
            raise LoRaWAN_Exception("All channels are busy.")
         elif RESPONSE["SILENT"] in rx:
            self._logger.debug("{}@Send/LoRaWAN: Silent".format(self._full_path))
            raise LoRaWAN_Exception("The module is in a Silent Immediately state.")
         elif RESPONSE["FC_ERR"] in rx:
            self._logger.debug("{}@Send/LoRaWAN: Frame counter error".format(self._full_path))
            raise LoRaWAN_Exception("The frame counter rolled over.")
         elif RESPONSE["MAC_PAUSED"] in rx:
            self._logger.debug("{}@Send/LoRaWAN: Mac paused".format(self._full_path))
            raise LoRaWAN_Exception("The LoRaWAN mode is paused.")
         elif RESPONSE["INVALID_DATA_LEN"] in rx:
            self._logger.debug("{}@Send/LoRaWAN: Invalid data length".format(self._full_path))
            raise LoRaWAN_Exception("The payload length is greater than the maximum in the current data rate.")
         else:
            self._logger.debug("{}@Send/LoRaWAN: Unknown error".format(self._full_path))
            raise LoRaWAN_Exception("Unknown error while transmitting the data.")

   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="a{sv}")
   def Receive(self):
      self._logger.debug("{}@Receive: Receive INIT".format(self._full_path))
      if not self._getConnected():
         self._logger.debug("{}@Receive: Module is not connected".format(self._full_path))
         raise LoRaWAN_Exception("Module is not connected.")
      result = {}
      # LoRa mode
      if self._setup[SETUP["MODE"]] == LORA_MODE:
         # Pause LoRaWAN mode
         self._module.write(CMD["MAC_PAUSE"])
         time.sleep(GUARDTIME["PAUSE"])
         rx = self._module.readline()
         try:
            if int(rx) > MIN_LORA_TIME:
               # Receive the message
               self._module.write(CMD["RAD_RX"])
               time.sleep(GUARDTIME["SET"])
               rx = self._module.readline()
               if RESPONSE["OK"] in rx:
                  # Change timeout for reception to the LoRa WDT
                  self._module.timeout = LORA_RX_TIMEOUT
                  time.sleep(GUARDTIME["RECEIVE"])
                  rx = self._module.readline()
                  self._module.timeout = TIMEOUT
                  if RESPONSE["RAD_RX"] in rx:
                     # Save the data discarting starting "radio_rx  " and the ending "\r\n"
                     self._logger.debug("{}@Receive/LoRa: Received={}".format(self._full_path, rx[10:-2]))
                     result[SENDRADPARAM["DATA"]] = rx[10:-2]
                  elif RESPONSE["RAD_ERR"] in rx:
                     # Timeout
                     self._logger.debug("{}@Receive/LoRa: Reception not succesful (timeout)".format(self._full_path))
                     raise LoRaWAN_Exception("The reception was not successful (timeout).")
                  else:
                     self._logger.debug("{}@Receive/LoRa: Received OK but unknown error".format(self._full_path))
                     raise LoRaWAN_Exception("Unknown error after receiving the data.")
               elif RESPONSE["BUSY"] in rx:
                  self._logger.debug("{}@Receive/LoRa: Busy".format(self._full_path))
                  raise LoRaWAN_Exception("The module is currently busy.")
               elif RESPONSE["INVALID_PARAM"] in rx:
                  self._logger.debug("{}@Receive/LoRa: Invalid param".format(self._full_path))
                  raise LoRaWAN_Exception("Invalid parameter in the radio rx command.")
               else:
                  self._logger.debug("{}@Receive/LoRa: Unknown error".format(self._full_path))
                  raise LoRaWAN_Exception("Unknown error while receiving the data.")
         except ValueError:
            self._logger.debug("{}@Receive/LoRa: Could not pause the module to use LoRa mode".format(self._full_path))
            raise LoRaWAN_Exception("Could not pause the module to use LoRa mode.")
         # Restore LoRaWAN mode
         finally:
            self._module.write(CMD["MAC_RESUME"])
            time.sleep(GUARDTIME["SET"])
            rx = self._module.readline()
      # LoRaWAN mode
      else:
         self._logger.debug("{}@Receive/LoRaWAN: Cannot receive data in LoRaWAN mode".format(self._full_path))
         raise LoRaWAN_Exception("Cannot receive data in LoRaWAN mode.")
      return dbus.Dictionary(result, signature="sv")
# -----------------------


