#!/usr/bin/python

import threading
import struct
import logging
from struct import *

# Thread for waiting for a call from gerris, execute the controller and return the result.
class FunctionController(threading.Thread):
	def __init__(self,callFifo,returnFifo,src,lock,forcesList,locMap):
		super(FunctionController,self).__init__()
		self.callFifo = callFifo
		self.returnFifo = returnFifo
		self.src = src
		self.lock = lock
		self.forcesList = forcesList
		self.locMap = locMap
		
	def run(self):
		toRead = Struct('i32s')
		toWrite = Struct('d32s')
		
		while True:
			try:
				query = self.callFifo.read(toRead.size) # 36 B
				querySt = toRead.unpack(query)
				queryType = querySt[0] 
				funcName = querySt[1].rstrip(' \t\r\n\0')
				logging.debug("Calling controller - Function=%s" % funcName)
				try:
					func = getattr(self.src, str(funcName))
				except AttributeError:
					logging.error("Function \"%s\" not found at \"%s\"." % (funcName, self.src))
					raise
				self.lock.acquire()
				result = func(self.forcesList,self.locMap)
				self.lock.release()
				length = len(funcName)
				s = toWrite.pack(result,funcName)
				
				logging.debug("Returning controller result - %s=%f" % (funcName, result))
				self.returnFifo.write(s)
			except struct.error as e:
				logging.warning("Error detected in send-receive information. The control loop will resume despite that.")
				return
