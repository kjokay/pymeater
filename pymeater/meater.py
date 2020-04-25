#!/bin/env python3

from bluepy import btle
import time

HANDLE_TEMP = 0x24
HANDLE_BATTERY = 0x28

class MeaterProbe(object):
    
    def __init__(self, addr):
        self.__addr = addr
        self.__firmware = None
        self.__ambient = -1
        self.__tip = -1
        self.__id = -1

        self.connect()
        self.update()

    @classmethod
    def scan(cls):
        '''
        '''
        scanner = btle.Scanner()

        for entry in scanner.scan(5):
            name = entry.getValueText(9)

            if(name is not None and 'MEATER' in name):
                print('found a meater at address {0}'.format(entry.addr))

                return MeaterProbe(entry.addr)
        
        return None

    @staticmethod
    def bytesToInt(byte0, byte1):
        return byte1*256+byte0

    @staticmethod
    def convertAmbient(array):
        tip = MeaterProbe.bytesToInt(array[0], array[1])
        ra  = MeaterProbe.bytesToInt(array[2], array[3])
        oa  = MeaterProbe.bytesToInt(array[4], array[5])
        return int(tip+(max(0,((((ra-min(48,oa))*16)*589))/1487)))

    @staticmethod
    def toCelsius(value):
        return (float(value)+8.0)/16.0

    @staticmethod
    def toFahrenheit(value):
        return ((MeaterProbe.toCelsius(value)*9)/5)+32.0

    @property
    def tip(self):
        return self.__tip

    def getTipF(self):
        return MeaterProbe.toFahrenheit(self.__tip)

    def getTipC(self):
        return MeaterProbe.toCelsius(self.__tip)

    def getAmbientF(self):
        return MeaterProbe.toFahrenheit(self.__ambient)

    @property
    def ambient(self):
        return self._ambient

    def getAmbientC(self):
        return MeaterProbe.toCelsius(self.__ambient)

    @property
    def battery(self):
        return self.__battery

    @property
    def address(self):
        return self.__addr

    @property
    def id(self):
        return self.__id

    @property
    def firmware(self):
        return self.__firmware

    def connect(self):
        self._dev = btle.Peripheral(self.__addr)

    def readCharacteristic(self, c):
      return bytearray(self._dev.readCharacteristic(c))

    def update(self):
        #for i in range(1, 64):
        #    print((i, str(self.readCharacteristic(i))))

        tempBytes = self.readCharacteristic(HANDLE_TEMP)        
        self.__tip = MeaterProbe.bytesToInt(tempBytes[0], tempBytes[1])
        self.__ambient = MeaterProbe.convertAmbient(tempBytes)

        batteryBytes = self.readCharacteristic(HANDLE_BATTERY)
        self.__battery = MeaterProbe.bytesToInt(batteryBytes[0], batteryBytes[1])*10

        #(self.__firmware, self.__id) = str(self.readCharacteristic(22)).split("_")
        print(str(self.readCharacteristic(22)).split("_"))

        self._lastUpdate = time.time()

    def __str__(self):
        return "%s %s probe: %s tip: %fF/%fC ambient: %fF/%fC battery: %d%% age: %ds" \
                % (self.address, self.firmware, self.id \
                , self.getTipF(), self.getTipC(), self.getAmbientF() \
                , self.getAmbientC(), self.battery \
                , time.time() - self._lastUpdate)

if(__name__ == '__main__'):
    #meater = MeaterProbe()
    meater = MeaterProbe.scan()

    for i in range(2):
        print(meater)
        time.sleep(1)
        meater.update()

