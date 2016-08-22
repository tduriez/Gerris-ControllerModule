#!/usr/bin/python

import os
import sys, getopt
import importlib
import threading
import logging
import collections
from communications import ControllerThread, CollectorThread
from samples import SamplesData

controllerFolder = 'python/user'
controllerModuleName = 'controller'
samplesWindow = 1
mpiproc = 0

#Communicate with another process through named pipes
#one for receive command, the other for send command, and the last one to receive values
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
		samplesWindow = int(arg)
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
sys.path.append(controllerFolder)
controlFunc = importlib.import_module(controllerModuleName)

samples = SamplesData(samplesWindow)
lock = threading.Lock()

# Create Values and Function threads.
collectorThread = CollectorThread(valuesFifo, samples, lock)
controllerThread = ControllerThread(callFifo, returnFifo, samples, lock, controlFunc)

collectorThread.start()
controllerThread.start()
collectorThread.join()
controllerThread.join()

logging.info("Closing FIFOS")
callFifo.close()
returnFifo.close()
valuesFifo.close()
logging.info("Python server finished")

