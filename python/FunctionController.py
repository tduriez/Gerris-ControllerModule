#!/usr/bin/python

import threading
from struct import *

# Thread for waiting for a call from gerris, execute the controller and return the result.
class FunctionController(threading.Thread):
	def __init__(self,callFifo,returnFifo,src,lock,forcesList,locMap, debug):
		super(FunctionController,self).__init__()
		self.callFifo = callFifo
		self.returnFifo = returnFifo
		self.src = src
		self.lock = lock
		self.forcesList = forcesList
		self.locMap = locMap
		self.debug = debug
		
	def run(self):
		toRead = Struct('i32s')
		toWrite = Struct('d32s')
		
		while True:
			try:
				query = self.callFifo.read(toRead.size) # 36 B
				querySt = toRead.unpack(query)
				queryType = querySt[0] 
				funcName = querySt[1].rstrip(' \t\r\n\0')
				if self.debug:
					print "Called Func Name %s" % funcName
				funcion = getattr(self.src, str(funcName))
				self.lock.acquire()
				result = funcion(self.forcesList,self.locMap)
				self.lock.release()
				length = len(funcName)
				s = toWrite.pack(result,funcName)
				
				if self.debug:
					print "Sending %f %s" % (float(result), funcName)
				self.returnFifo.write(s)
			except:
				return	
