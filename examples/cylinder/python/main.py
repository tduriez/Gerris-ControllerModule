#!/usr/bin/python

import os
import sys, getopt
import importlib
import threading
import logging
import collections
import re
from communications import ControllerThread, CollectorThread
from samples import SamplesData

samplesWindow = 1
mpiproc = 0

#Communicate with another process through named pipes
#one for receive command, the other for send command, and the last one to receive values
callFifoFilepath = ''
returnFifoFilepath = ''
valuesFifoFilepath = ''


try:
    opts, args = getopt.getopt(sys.argv[1:],'', ['script=', 'samples=','mpiproc=', 'requestfifo=', 'returnfifo=', 'samplesfifo=', 'loglevel='])
except getopt.GetoptError:
    sys.stderr.write("Python **: Error invoking main.py.\nSample command line: ./main.py --script <scriptFilepath> --samples <numberOfSamplesInControllingWindow> --mpiproc <processId> --requestfifo <filepath> --returnfifo <filepath> --samplesfifo <filepath> --loglevel (debug|info|warning|error)")
    raise
if not opts or len(opts) < 6:
    sys.stderr.write("Python **: Error invoking main.py. Required arguments: --script --samples --mpiproc --requestfifo --returnfifo --samplesfifo --loglevel")
    sys.exit(1)
for opt, arg in opts:
    if opt == '--script':
        userScript = arg
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
    elif opt == '--loglevel':
        logLevelStr = arg
try:
    logLevel = getattr(logging, logLevelStr.upper())
except AttributeError:
    sys.stderr.write("Python **: Error configuring logging level to: %s. Valid values are 'debug', 'info', 'warning', 'error'" % logLevelStr)
    raise
logging.basicConfig(format='%(asctime)s Python %(levelname)s **: PE=' + str(mpiproc) + ' - %(message)s', level=logLevel)

logging.info("Opening Gerris2Python FIFO at %s" % callFifoFilepath)
callFifo = open(callFifoFilepath, 'r')
logging.info("Opening Python2Gerris FIFO at %s" % returnFifoFilepath)
returnFifo = open(returnFifoFilepath, 'w',0)
logging.info("Opening Gerris2Python FIFO for actuation values at %s" % valuesFifoFilepath)
valuesFifo = open(valuesFifoFilepath, 'r')
value = 0

# Load functions defined by user.
scriptMatch = re.match(r'^(.*)/(.*)\.py$', userScript)
if not scriptMatch:
    msg = "The given user script location is not valid. Provided path: %s. Expected pattern: <module-folder>/<filename>.py" % userScript
    logging.error(msg)
    raise ValueError(msg)

controllerFolder = scriptMatch.group(1)
controllerModuleName = scriptMatch.group(2)
sys.path.append(controllerFolder)
controlFunc = importlib.import_module(controllerModuleName)

samples = SamplesData(samplesWindow)
lock = threading.Lock()

# Create Values and Function threads.
collectorThread = CollectorThread(valuesFifo, samples, lock)
controllerThread = ControllerThread(callFifo, returnFifo, samples, lock, controlFunc)

collectorThread.start()
controllerThread.start()
try:
    collectorThread.join()
    controllerThread.join()
    logging.info("Simulation finished. Closing FIFOs...")
    callFifo.close()
    returnFifo.close()
    valuesFifo.close()
    logging.info("Python server finished")
except KeyboardInterrupt:
    logging.error("Keyboard signal detected. Aborting tasks to close the server...")
    raise
