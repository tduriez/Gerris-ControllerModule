import threading
import struct
import logging
from struct import *
from samples import Sample, ForceData, ProbeData

def _readBlock(f, blockSize):
    readBytes = 0
    result = ''
    while readBytes < blockSize:
        partResult = f.read(blockSize - readBytes)
        partReadBytes = len(partResult)
        if partReadBytes == 0:
            return None
        else:
            readBytes += partReadBytes
            result += partResult
    return result

# Thread for waiting for a call from gerris, execute the controller and return the result.
class ControllerThread(threading.Thread):
    def __init__(self, callFifo, returnFifo, samples, lock, controlModule):
        super(ControllerThread,self).__init__()
        self.callFifo = callFifo
        self.returnFifo = returnFifo
        self.samples = samples
        self.lock = lock
        self.controlModule = controlModule

    def run(self):
        toRead = Struct('i32s')
        toWrite = Struct('d32s')

        fifoOpened = True
        while fifoOpened:
            logging.debug("ControllerThread - Waiting for call request...")
            query = _readBlock(self.callFifo, toRead.size) # 36 B
            if query is None:
                fifoOpened = False
            else:
                try:
                    querySt = toRead.unpack(query)
                    queryType = querySt[0]
                    funcName = querySt[1].rstrip(' \t\r\n\0')

                    func = self._get_function(funcName)
                    self.lock.acquire()
                    result = func(self.samples)
                    self.lock.release()
                    length = len(funcName)
                    s = toWrite.pack(result,funcName)

                    logging.debug("ControllerThread - Returning controller result - %s=%f" % (funcName, result))
                    self.returnFifo.write(s)
                except struct.error as e:
                    logging.error('Parsing error. Invalid struct data received. Data=%s', query)
                    raise
        logging.info('Call requests FIFO closed. Finishing controller...')

    def _get_function(self, funcName):
        logging.debug("ControllerThread - Calling controller - Module=%s Function=%s" % (self.controlModule, funcName))
        try:
            return getattr(self.controlModule, funcName)
        except AttributeError:
            logging.error("Function \"%s\" not found at \"%s\". DetectedFunctions=%s" % (funcName, self.controlModule, dir(self.controlModule)))
            raise

# Thread for reading the sent values from gerris.
class CollectorThread(threading.Thread):
    def __init__(self, valuesFifo, samples, lock):
        super(CollectorThread,self).__init__()
        self.valuesFifo = valuesFifo
        self.samples = samples
        self.lock = lock

    def run(self):
        toRead = Struct('idi12d')
        toReadLoc = Struct('idi4d64s')
        fifoOpened = True
        while fifoOpened:
            logging.debug("CollectorThread- Waiting for samples information...")
            query = _readBlock(self.valuesFifo, toRead.size)
            if query is None:
                fifoOpened = False
            else:
                try:
                    querySt = toRead.unpack(query)
                    if (querySt[0] == 0):   # type: 0 force
                        self.handleForce(querySt)
                    elif (querySt[0] == 1): #type: 1 location
                        querySt = toReadLoc.unpack(query)
                        self.handleLocation(querySt)
                    else:
                        msg = 'Invalid struct type. Type=%d is not recognized as Force or Location sample. Data=%s' % (querySt[0], query)
                        logging.error(msg)
                        raise SyntaxError(msg)
                except struct.error as e:
                    logging.error('Parsing error. Invalid struct data received. Data=%s', query)
                    raise
        logging.info('Samples information FIFO closed. Finishing controller...')

    def handleForce(self, querySt):
        time = querySt[1]
        step = querySt[2]
        pf = (querySt[3],querySt[4],querySt[5])
        vf = (querySt[6],querySt[7],querySt[8])
        pm = (querySt[9],querySt[10],querySt[11])
        vm = (querySt[12],querySt[13],querySt[14])
        sample = Sample(time, step, ForceData(pf, vf, pm, vm))
        logging.debug("CollectorThread- Handling force value. step=%d - time=%.3f - pf=%s - ..."
                      % (step, time, pf))
        self.lock.acquire()
        self.samples.addForce(sample)
        self.lock.release()

    def handleLocation(self, querySt):
        time = querySt[1]
        step = querySt[2]
        value = querySt[3]
        location = (querySt[4],querySt[5],querySt[6])
        variable = querySt[7].rstrip(' \t\r\n\0')
        sample = Sample(time, step, ProbeData(location, variable, value))
        logging.debug("CollectorThread- Handling location value. step=%d - time=%.3f - location=%s - variable=%s - value=%f"
                      % (step, time, location, variable, value))
        self.lock.acquire()
        self.samples.addProbe(sample)
        self.lock.release()

