#!/usr/bin/python

import threading
from struct import *
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
		
# Class for storing a given value from gerris. It can be either a location or a force value.
class ValueControl(object):
	def __init__(self,time,step,data):
		#self.valType = valType
		self.time = time
		self.step = step
		self.data = data

# Thread for reading the sent values from gerris.
class ValuesController(threading.Thread):
	def __init__(self,fifo,forcesList,locationsList,lock,length,debug):
		super(ValuesController,self).__init__()
		self.fifo = fifo
		self.forcesList = forcesList
		self.locationsList = locationsList
		self.lock = lock
		self.length = int(length)
		self.debug = debug
		
	def run(self):
		toRead = Struct('idi12d')
		toReadLoc = Struct('idi4d64s')
		while True:
			try:
				query = self.fifo.read(toRead.size) # 112 B
				querySt = toRead.unpack(query)
				if self.debug:
					print querySt
					print "type"
					print querySt[0]
				if (querySt[0] == 0):	# type: 0 force
					# print debug info if needed
					self.printForce(querySt)
					self.lock.acquire()
					# guardo valores en forcesList
					fVal = ForceValue(\
						(querySt[3],querySt[4],querySt[5]),\
						(querySt[6],querySt[7],querySt[8]),\
						(querySt[9],querySt[10],querySt[11]),\
						(querySt[12],querySt[13],querySt[14]))
					new = ValueControl(querySt[1],querySt[2],fVal)
					self.forcesList.append(new)
					# Remove old value			
					if len(self.forcesList) > self.length:
						self.forcesList.popleft()
					self.lock.release()
					if self.debug:
						print "Force guardada"
					
				elif (querySt[0] == 1): #type: 1 location
					querySt = toReadLoc.unpack(query)
					# print debug info if needed
					self.printLocation(querySt)
					self.lock.acquire()
					# guardo valores en locationsMap
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
						
					# remove old value
					if len(self.locationsList) > self.length:
						self.locationsList.popleft()
					self.lock.release()
					if self.debug:
						print "Location guardada"
				else:
					print "Error de tipo de valor a guardar"
			except:
				return

	def printForce(self, querySt):
		 if self.debug:
			print "Type FORCE"
                        print "time"
                        print querySt[1]
                        print "step"
                        print querySt[2]
                        print "pfx"
                        print querySt[3]
                        print "pfy"
                        print querySt[4]
                        print "pfz"
                        print querySt[5]
                        print "vfx"
                        print querySt[6]
                        print "vfy"
                        print querySt[7]
                        print "vfz"
                        print querySt[8]
                        print "pmx"
                        print querySt[9]
                        print "pmy"
                        print querySt[10]
                        print "pmz"
                        print querySt[11]
                        print "vmx"
                        print querySt[12]
                        print "vmy"
                        print querySt[13]
                        print "vmz"
                        print querySt[14]

	def printLocation(self, querySt):
		 if self.debug:
	                 print "Type LOCATION"
                         print querySt
                         print "type"
                         print querySt[0]
                         print "time"
                         print querySt[1]
                         print "step"
                         print querySt[2]
                         print "value"
                         print querySt[3]
                         print "pos0"
                         print querySt[4]
                         print "pos1"
                         print querySt[5]
                         print "pos2"
                         print querySt[6]
                         print "varname"
                         print querySt[7]

