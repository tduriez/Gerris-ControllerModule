#!/usr/bin/python

import os
import sys, getopt
import imp
import threading
import logging
import collections
import FunctionController
import ValuesController

#communicate with another process through named pipes
#one for receive command, the other for send command
#one to receive values

scriptPath = "./module"
cant = 1
mpiproc = 0

callFifoFilepath = ''
returnFifoFilepath = ''
valuesFifoFilepath = ''


try:
	opts, args = getopt.getopt(sys.argv[1:],'', ['script=', 'samples=','mpiproc=', 'requestfifo=', 'returnfifo=', 'samplesfifo='])
except getopt.GetoptError:
	sys.stderr.write("Python **: main.py --script <scriptFilepath> --samples <numberOfSamplesInControllingWindow> --mpiproc <processId> --requestfifo <filepath> --returnfifo <filepath> --samplesfifo <filepath>")
	sys.exit(1)
if not opts or len(opts) < 6:
	sys.stderr.write("Python **: Error invoking main.py. Required arguments: --script --samples --mpiproc --requestfifo --returnfifo --samplesfifo")
	sys.exit(2)
for opt, arg in opts:
	if opt == '--script':
		scriptPath = arg
	elif opt == '--samples':
		cant = int(arg)
	elif opt == '--mpiproc':
		mpiproc = int(arg)
	elif opt == '--requestfifo':
		callFifoFilepath = arg
	elif opt == '--returnfifo':
		returnFifoFilepath = arg
	elif opt == '--samplesfifo':
		valuesFifoFilepath = arg


logging.basicConfig(format='%(asctime)s Python %(levelname)s **: PE=' + str(mpiproc) + ' - %(message)s', level=logging.DEBUG)

logging.info("Opening Gerris2Python FIFO at %s" % callFifoFilepath)
callFifo = open(callFifoFilepath, 'r')
logging.info("Opening Python2Gerris FIFO at %s" % returnFifoFilepath)
returnFifo = open(returnFifoFilepath, 'w',0)
logging.info("Opening Gerris2Python FIFO for actuation values at %s" % valuesFifoFilepath)
valuesFifo = open(valuesFifoFilepath, 'r')
value = 0

# Load functions defined by user.
foo = imp.load_source('script', scriptPath)


forcesValues = collections.deque()
locationsValues = collections.deque()
lock = threading.Lock()

# Create Values and Function threads.
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

logging.info("Closing FIFOS")
callFifo.close()
returnFifo.close()
valuesFifo.close()
logging.info("Python server finished")

