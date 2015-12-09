#!/usr/bin/python

import threading
from struct import *

class FunctionController(threading.Thread):
	def __init__(self,callFifo,returnFifo,src):
		super(FunctionController,self).__init__()
		self.callFifo = callFifo
		self.returnFifo = returnFifo
		self.src = src
		
	def run(self):
		toRead = Struct('i32s')
		
		while True:
			#try:
				print toRead.size
				query = self.callFifo.read(toRead.size) # 36 B
				querySt = toRead.unpack(query)
				queryType = querySt[0] 
				print "Query type %d" % queryType
				funcName = querySt[1].rstrip(' \t\r\n\0')
				print "Func Name %s" % funcName
				funcion = getattr(self.src, str(funcName))
				result = funcion(4)
				length = len(funcName)
				s = struct.pack('d32s' ,result,funcName)
				print "Sending %i %s" % result, funcName
				print len(s)
				self.returnFifo.write(s)
			#except:
				#print "Error en FunctionController"
				#return	
