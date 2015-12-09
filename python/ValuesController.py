#!/usr/bin/python

import threading
from struct import *

class ForceValue(object):
	def __init__(self,pf,vf,pm,vm):
		self.pf = pf
		self.vf = vf
		self.pm = pm
		self.vm = vm
		
class LocationValue(object):
	def __init__(self,varName,value,position):
		self.varName = varName
		self.value = value
		self.position = position
		
class ValueControl(object):
	def __init__(self,valType,time,step,data):
		#self.valType = valType
		self.time = time
		self.step = step
		self.data = data

class ValuesController(threading.Thread):
	def __init__(self,fifo,forcesList,locationsMap,forcesLock,locationsLock):
		super(ValuesController,self).__init__()
		self.fifo = fifo
		self.forcesList = forcesList
		self.locationsMap = locationsMap
		self.forcesLock = forcesLock
		self.locationsLock = locationsLock
		
	def run(self):
		toRead = Struct('idi12d')
		while True:
			#try:
				print toRead.size
				query = self.fifo.read(toRead.size) # 112 B
				querySt = toRead.unpack(query)
				print querySt
				print querySt[0]
				print querySt[1]
				print querySt[2]
				print querySt[3]
				print querySt[4]
				print querySt[5]
				print querySt[6]
				print querySt[7]
				print querySt[8]
				print querySt[9]
				print querySt[10]
				print querySt[11]
				print querySt[12]
				print querySt[13]
				print querySt[14]
				print querySt[15]
				if (querySt[0] == 0):	# type: 0 force
					print "Type FORCE"
					self.forcesLock.acquire()
					# guardo valores en forcesList
					self.forcesLock.release()
				elif (querySt[0] == 1): #type: 1 location
					print "Type LOCATION"
					self.locationsLock.acquire()
					# guardo valores en locationsMap
					self.locationsLock.release()
				else:
					print "Error de tipo de valor a guardar"
			#except:
				#print "Error en ValuesController"
				#return
