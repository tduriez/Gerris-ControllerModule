#!/usr/bin/python
import threading
import struct
from struct import *
import logging
import collections

# Class for storing a given force value from gerris.
class ForceValue(object):
    def __init__(self,pf,vf,pm,vm):
        self.pf = pf
        self.vf = vf
        self.pm = pm
        self.vm = vm

# Class for storing a given Location value from gerris
class LocationValue(object):
    def __init__(self):
        #self.varName = varName
        self.varMap = {}
    def addValue(self, varName, pos, value):
        values = self.varMap.get(varName)
        if values == None:
            values = []
            self.varMap[varName] = values
        values.append((pos,value))
    def getVariables(self):
        return self.varMap.keys()
    def getValues(self, variable):
        return self.varMap.get(variable)

# Class for storing a given value from gerris. It can be either a location or a force value.
class ValueControl(object):
    def __init__(self,time,step,data):
        #self.valType = valType
        self.time = time
        self.step = step
        self.data = data

# Thread for reading the sent values from gerris.
class ValuesController(threading.Thread):
    def __init__(self,fifo,forcesList,locationsList,lock,length):
        super(ValuesController,self).__init__()
        self.fifo = fifo
        self.forcesList = forcesList
        self.locationsList = locationsList
        self.lock = lock
        self.length = int(length)

    def run(self):
        toRead = Struct('idi12d')
        toReadLoc = Struct('idi4d64s')
        while True:
            try:
                query = self.fifo.read(toRead.size)
                querySt = toRead.unpack(query)
                if (querySt[0] == 0):   # type: 0 force
                    self.handleForce(querySt)
                elif (querySt[0] == 1): #type: 1 location
                    querySt = toReadLoc.unpack(query)
                    self.handleLocation(querySt)

                else:
                    print "Error de tipo de valor a guardar"
            except struct.error as e:
                return

    def handleForce(self, querySt):
        self.lock.acquire()
        fVal = ForceValue(\
            (querySt[3],querySt[4],querySt[5]),\
            (querySt[6],querySt[7],querySt[8]),\
            (querySt[9],querySt[10],querySt[11]),\
            (querySt[12],querySt[13],querySt[14]))
        new = ValueControl(querySt[1],querySt[2],fVal)
        self.forcesList.append(new)
        # Remove old value if necessary
        if len(self.forcesList) > self.length:
            self.forcesList.popleft()
        self.lock.release()

    def handleLocation(self, querySt):
        self.lock.acquire()
        locVal = None
        for loc in self.locationsList:
            if loc.step == querySt[2]:
                locVal = loc
                break

        if (locVal == None):
            loc = LocationValue()
            locVal = ValueControl(querySt[1],querySt[2],loc)
            self.locationsList.append(locVal)

        locVal.data.addValue(querySt[7].rstrip(' \t\r\n\0'),(querySt[4],querySt[5],querySt[6]),querySt[3])

        if len(self.locationsList) > self.length:
            self.locationsList.popleft()
        self.lock.release()

