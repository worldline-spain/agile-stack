
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
#            AGILE DBus Protocol XBee ZigBee            #
#                                                       #
#    Description: Class of the Protocol defined in the  #
#       in the AGILE API with the implementation of the #
#       XBee ZigBee protocol.                           #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.2                                       #
#    Date: August 2016                                  #
#########################################################

# --- Imports -----------
import dbus
import dbus.service
from dbus_protocols import dbus_protocol as dbP
from dbus_protocols import dbus_constants as db_cons
import logging
import serial
import xbee

import struct
import time
import datetime
import json

# -----------------------


# --- Variables ---------
PROTOCOL_NAME = "XBee_ZigBee"
BAUDRATE = "baudrate"
DEF_BAUDRATE = 9600
APIMODE2 = "apiMode2"
DEF_APIMODE2 = True
ATCMDS = "atCmds"
APITXCMDS = ["at", "queued_at", "remote_at", "tx_long_addr", "tx", "tx_explicit"]
CMDWRITE = b"WR"
# -----------------------


# --- Classes -----------
class XBee_ZigBee(dbP.Protocol):
   
   def __init__(self):     
      super().__init__()
      self._protocol_name = PROTOCOL_NAME
      self._objS0 = XBee_ZigBee_Obj(self._socket0)
      self._objS1 = XBee_ZigBee_Obj(self._socket1)
       

class XBee_ZigBee_Exception(dbP.ProtocolException):
   
   def __init__(self, msg=""):
      super().__init__(PROTOCOL_NAME, msg)
      
    
class XBee_ZigBee_Obj(dbP.ProtocolObj):

   def __init__(self, socket):
      super().__init__(PROTOCOL_NAME, socket)
      self._setup = {
         BAUDRATE: DEF_BAUDRATE,
         APIMODE2: DEF_APIMODE2,
         ATCMDS: []
      }
      self._last_read_for_device = dict()

   def async_data_callback(self, data):
      hex_long_addr = format(struct.unpack(">Q", data["source_addr_long"])[0], '016x')
      str_tstamp = time.strftime('%Y-%m-%d %H:%M:%S')

      # decode received data with the format SensorNum - SensorType - SensorVal - Counter (01-Motion-ON-0)
      raw_sensor_data = data["rf_data"].decode("utf-8")
      # raw_sensor_data = raw_sensor_data.replace("PUT_DATE", str_tstamp)
      cooked_data = json.loads(raw_sensor_data)
      
      if hex_long_addr in self._last_read_for_device: 
         device_data = self._last_read_for_device[hex_long_addr]
      else:
         device_data = dict()
      
      cooked_data["data"]["date"] = str_tstamp
      sensor_type = cooked_data["type"]
      
      cooked_data["id"] = hex_long_addr + "_" + sensor_type
      
      if sensor_type == "beacon":
        print("beacon data detected!!")
        
        if sensor_type in device_data.keys():
            beacon_list_str=device_data[sensor_type];
        else:
            beacon_list_str = "[]";
        
        beacon_list=json.loads(beacon_list_str)
        
        #filtrar los beacons con data.date que tengan mas de 10 segundos de vida y que tengan el mismo beacon id, major y minor
        self.PurgeBeaconList(beacon_list,cooked_data["data"]["value"]["ibeaconid"],cooked_data["data"]["value"]["major"],cooked_data["data"]["value"]["minor"])
        
        beacon_list.append(cooked_data["data"])
        
        dump_cooked_data = json.dumps(beacon_list)
      else:
        dump_cooked_data = json.dumps(cooked_data)
      
      print("raw_sensor_data", raw_sensor_data, " -> ", dump_cooked_data) 
      device_data[sensor_type] = dump_cooked_data
      # device_data[sensor_num] = sensor_data
      self._last_read_for_device[hex_long_addr] = device_data
      
      
   def PurgeBeaconList(self,beacon_list,beaconId,major,minor):

        secondspurgeTimestamp=(datetime.datetime.now()-datetime.timedelta(seconds=30))

        beacon_delete_list=[];
        
        for beacon in beacon_list:
            if ((beacon["value"]["ibeaconid"]==beaconId) and (beacon["value"]["major"]==major) and (beacon["value"]["minor"]==minor)):
                beacon_delete_list.append(beacon)
            else:
                if  (datetime.datetime.strptime(beacon["date"], '%Y-%m-%d %H:%M:%S')< secondspurgeTimestamp):   
                    beacon_delete_list.append(beacon)
        
        for beacon in beacon_delete_list:
            beacon_list.remove(beacon)
           
            
       
   # Override DBus object methods
   @dbus.service.method(db_cons.BUS_NAME, in_signature="s", out_signature="")
   def Connect(self, deviceId):
      if self._getConnected():
         raise XBee_ZigBee_Exception("Module is already connected.")
      self._serial = serial.Serial(self._getSocketDev(self._socket), self._setup[BAUDRATE])
      self._module = xbee.ZigBee(self._serial, escaped=self._setup[APIMODE2], callback=self.async_data_callback)
      writeChanges = False
      for option in self._setup[ATCMDS]:
         cmd = list(option.keys())[0]
         param = list(option.values())[0]
         cmdEnc = cmd.encode("UTF-8")
         if (cmdEnc == CMDWRITE):
            writeChanges = True
            break
         paramEnc = b"\x00"
         blen = (param.bit_length() + 7) // 8
         if blen != 0:
            paramEnc = param.to_bytes(blen, byteorder="big")
         self._module.send("at", frame_id=b"R", command=cmdEnc, parameter=paramEnc)
         rx = self._module.wait_read_frame()
         if not rx["status"]:
            raise XBee_ZigBee_Exception("Did not receive response from AT command")
         if rx["status"] != b"\x00":
            raise XBee_ZigBee_Exception("Wrong AT command/parameter ({}/{})".format(cmd, param))
      if writeChanges:
         self._module.send("at", frame_id=b"R", command=CMDWRITE)
         rx = self._module.wait_read_frame()
         if not rx["status"]:
            raise XBee_ZigBee_Exception("Did not receive response from AT command")
      self._setConnected(True)

   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="")
   def Disconnect(self):
      if not self._getConnected():
         raise XBee_ZigBee_Exception("Module is already disconnected.")
      self._setConnected(False)
      self._module.halt()
      self._serial.close()

   @dbus.service.method(db_cons.BUS_NAME, in_signature="a{sv}", out_signature="")
   def Setup(self, args):
      self._setup.clear()
      self._setup = {
         BAUDRATE: DEF_BAUDRATE,
         APIMODE2: DEF_APIMODE2,
         ATCMDS: []
      }
      for key in args.keys():
         if key == BAUDRATE:
            self._setup[BAUDRATE] = int(args[BAUDRATE])
         elif key == APIMODE2:
            self._setup[APIMODE2] = bool(args[APIMODE2])
         else:
            try:
               param = int(args[key], 16)              
            except ValueError:
               param = 0x00
            finally:
               self._setup[ATCMDS].append({str(key): param})
         
   @dbus.service.method(db_cons.BUS_NAME, in_signature="a{sv}", out_signature="")
   def Send(self, args):
      if not self._getConnected():
         raise XBee_ZigBee_Exception("Module is not connected.")
      cmd = args.pop("api_command", "")
      if not cmd in APITXCMDS:
         raise XBee_ZigBee_Exception("A valid API command must be provided {}.".format(APITXCMDS))
      params = {}
      for key in args.keys():
         if type(args[key]) == dbus.Array:
            params[key] = bytes(args[key])
      self._module.send(cmd, **params)

   @dbus.service.method(db_cons.BUS_NAME, in_signature="", out_signature="a{sv}")
   def Receive(self):
      if not self._getConnected():
         raise XBee_ZigBee_Exception("Module is not connected.")
      rx = self._module.wait_read_frame()
      result = {}
      for key in rx.keys():
         result[key] = []
         for byte in rx[key]:
            result[key].append(byte)
      return dbus.Dictionary(result, signature="sv")
  
   @dbus.service.method(db_cons.BUS_NAME, in_signature="ss", out_signature="ay")
   def Read(self, deviceId, sensorName):
       if not self._getConnected():
           raise XBee_ZigBee_Exception("Module is not connected.")

       # deviceId is like xbee_zigbee0013a20040f9a03c : protocol name (lowercase) + device address !!!!!
       deviceId = deviceId.replace(PROTOCOL_NAME.lower(), "")
       rdata = "unknown"
       if isinstance(deviceId, str) and deviceId.lower() in self._last_read_for_device:
          if isinstance(sensorName, str) and sensorName in self._last_read_for_device[deviceId]:
             # for key, val in self._last_read_for_device[deviceId].items():
             # rdata += '{"deviceId":"'+deviceId+'","sensor_type":"'+val['sensor_type']+'","sensor_val":"'+val['sensor_val']+'","tstamp":"'+val['tstamp']+'"}'
             
             # rdata = (self._last_read_for_device[deviceId][sensorName]['sensor_type'] +
             #         "," + 
             #         self._last_read_for_device[deviceId][sensorName]['sensor_val'] +
             #         "," +
             #         self._last_read_for_device[deviceId][sensorName]['tstamp'])
             rdata = self._last_read_for_device[deviceId][sensorName]
       # print("--- Read device=", deviceId, " sensor=", sensorName, " rdata=", rdata)
       return bytearray(rdata, "ascii")
  
   @dbus.service.method(db_cons.BUS_NAME, in_signature="ss", out_signature="")
   def Write(self, deviceId, value):
       if not self._getConnected():
           raise XBee_ZigBee_Exception("Module is not connected.")
       rdata = ""

       # deviceId is like xbee_zigbee0013a20040f9a03c : protocol name (lowercase) + device address !!!!!
       deviceId = deviceId.replace(PROTOCOL_NAME.lower(), "")
       # print("--- Read device=", deviceId, " value=", value)
           
       self._module.send("tx", dest_addr_long=bytearray.fromhex(deviceId), data=bytearray(value, "ascii"))
       return

   
   @dbus.service.method(db_cons.BUS_NAME, in_signature="a{sv}", out_signature="") 
   def Discover(self, args):
      self._logger.log("test")
# -----------------------
