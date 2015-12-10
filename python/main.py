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
debug = False
try:
	opts, args = getopt.getopt(sys.argv[1:],"f:n:z")
except getopt.GetoptError:
	print "main.py -f <pathToFileScript> -n <numberOfPreviousValues>"
	sys.exit(1)
if not opts:
	print "Error: Required arguments: -f -n"
	sys.exit(2)
for opt, arg in opts:
	if opt == '-f':
		scriptPath = arg
	elif opt == '-n':
		cant = arg
	elif opt == '-z':
		debug = True

callPath = "/tmp/callfifo"
recvPath = "/tmp/recvfifo"
valuesPath = "/tmp/valuesfifo"
callFifo = open(callPath, 'r')
returnFifo = open(recvPath, 'w',0)
valuesFifo = open(valuesPath, 'r')
value = 0
foo = imp.load_source('script', scriptPath)


forcesValues = collections.deque()
locationsValues = collections.deque()
lock = threading.Lock()
valuesThread = ValuesController.ValuesController(valuesFifo,\
		forcesValues,\
		locationsValues,\
		lock,\
		cant, debug)
												
callThread = FunctionController.FunctionController(callFifo,\
						returnFifo,\
						foo,\
						lock,\
						forcesValues,\
						locationsValues, debug)

valuesThread.start()
callThread.start()

valuesThread.join()
callThread.join()

print "Termino"
callFifo.close()
returnFifo.close()
valuesFifo.close()
