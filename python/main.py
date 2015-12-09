#!/usr/bin/python

import os
#import struct
import imp
import threading
import FunctionController
import ValuesController

#communicate with another process through named pipe
#one for receive command, the other for send command
callPath = "/tmp/callfifo"
recvPath = "/tmp/recvfifo"
valuesPath = "/tmp/valuesfifo"
callFifo = open(callPath, 'r')
returnFifo = open(recvPath, 'w',0)
valuesFifo = open(valuesPath, 'r')
value = 0
foo = imp.load_source('script', './module/script.py')

"""while True:
	query = callFifo.read(36)
	querySt = struct.unpack('i32s', query)
	queryType = querySt[0] 
	print "Query type %d" % queryType
	funcName = querySt[1].rstrip(' \t\r\n\0')
	print "Func Name %s" % funcName
	funcion = getattr(foo, str(funcName))
	result = funcion(4)
	length = len(funcName)
	s = struct.pack('d32s' ,result,funcName)
	print "Sending %s" % s
	print len(s)
	returnFifo.write(s)		
"""

forcesValues = []
locationsValues = {}
forcesLock = threading.Lock()
locationsLock = threading.Lock()
valuesThread = ValuesController.ValuesController(valuesFifo,\
												forcesValues,\
												locationsValues,\
												forcesLock,\
												locationsLock)
												
callThread = FunctionController.FunctionController(callFifo,returnFifo,foo)

valuesThread.start()
callThread.start()

valuesThread.join()
callThread.join()

print "Termino"
callFifo.close()
returnFifo.close()
valuesFifo.close()
