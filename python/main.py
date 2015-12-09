#!/usr/bin/python

import os
import sys, getopt
#import struct
import imp
import threading
import collections
import FunctionController
import ValuesController

#communicate with another process through named pipes
#one for receive command, the other for send command
#one to receive values

scriptPath = "./"
cant = 1
try:
	opts, args = getopt.getopt(sys.argv[1:],"f:n:")
except getopt.GetoptError:
	print "main.py -f <pathToFileScript> -n <numberOfPreviousValues>"
	sys.exit(1)
if not opts:
	print "Error: Required arguments: -f -n"
	sys.exit(2)
for opt, arg in opts:
	if opt == '-f':
		scriptPath = arg
	elif opt == '.n':
		cant = arg

callPath = "/tmp/callfifo"
recvPath = "/tmp/recvfifo"
valuesPath = "/tmp/valuesfifo"
callFifo = open(callPath, 'r')
returnFifo = open(recvPath, 'w',0)
valuesFifo = open(valuesPath, 'r')
value = 0
foo = imp.load_source('script', scriptPath)

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

forcesValues = collections.deque()
locationsValues = {}
lock = threading.Lock()
valuesThread = ValuesController.ValuesController(valuesFifo,\
												forcesValues,\
												locationsValues,\
												lock,\
												cant)
												
callThread = FunctionController.FunctionController(callFifo,\
												returnFifo,\
												foo,\
												lock,\
												forcesValues,\
												locationsValues)

valuesThread.start()
callThread.start()

valuesThread.join()
callThread.join()

print "Termino"
callFifo.close()
returnFifo.close()
valuesFifo.close()
