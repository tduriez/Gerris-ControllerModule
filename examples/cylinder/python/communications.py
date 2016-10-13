import threading
import struct
import logging
import re
from struct import *
from samples import Sample, ForceData, ProbeData

_normalizeRegex = re.compile('^[_\-\w\d]+');
def _normalizeKeyword(string):
    result = _normalizeRegex.match(string)
    if result:
        return result.group(0)
    else:
        raise SyntaxError('It was not possible to identify a valid keyword in the received ' \
                        'string. Try with only digits and letters. Received string: "%r"' % string)

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
    logging.debug("Receiving %d bytes block: %r" % (blockSize, result))
    return result

class ExecutionContext:
    def __init__(self):
        self.lock = threading.Lock()
        self.errorsDetected = False

# Thread for waiting for a call from gerris, execute the controller and return the result.
class ControllerThread(threading.Thread):
    Request = Struct('di60s')
    Response = Struct('d')

    def __init__(self, callFifo, returnFifo, samples, controlModule, context):
        super(ControllerThread,self).__init__()
        self.callFifo = callFifo
        self.returnFifo = returnFifo
        self.samples = samples
        self.controlModule = controlModule
        self.context = context

    def run(self):
        fifoOpened = True
        try:
            while fifoOpened and not self.context.errorsDetected:
                logging.debug("ControllerThread - Waiting for call request... %d bytes" % self.Request.size)
                query = _readBlock(self.callFifo, self.Request.size)
                if query is None:
                    fifoOpened = False
                else:
                    self._processRequest(query)
            logging.info('Call requests FIFO closed. Finishing controller...')
        except Exception as e:
            logging.exception('ControllerThread - Closing with errors')
            self.context.errorsDetected = True

    def _processRequest(self, query):
        try:
            querySt = self.Request.unpack(query)
            time = querySt[0]
            step = querySt[1]
            funcName = _normalizeKeyword(querySt[2])

            func = self._get_function(funcName)
            with self.context.lock:
                result = func(time, step, self.samples)
            s = self.Response.pack(result)

            logging.debug("ControllerThread - Returning controller result - step=%d - t=%.3f - function=%s - result=%f"
                            % (step, time, funcName, result))
            self.returnFifo.write(s)
        except struct.error as e:
            logging.error('Parsing error. Invalid struct data received. Data=%s', query)
            raise

    def _get_function(self, funcName):
        logging.debug("ControllerThread - Calling controller - Module=%s Function=\"%r\"" % (self.controlModule, funcName))
        try:
            return getattr(self.controlModule, funcName)
        except AttributeError:
            logging.error("Function \"%r\" not found at \"%s\". DetectedFunctions=%s" % (funcName, self.controlModule, dir(self.controlModule)))
            raise

# Thread for reading the sent values from gerris.
class CollectorThread(threading.Thread):
    PKG_FORCE_VALUE = 0
    PKG_LOCATION_VALUE = 1
    PKG_META_VARIABLE = 2
    PKG_META_POSITION = 3

    ForceValue = Struct('=di3d3d3d3d')
    LocationValue = Struct('=di28sd3d')
    LocationMetaVariable = Struct('=i28s')
    LocationMetaPosition = Struct('=i3d')

    def __init__(self, valuesFifo, samples, context):
        super(CollectorThread,self).__init__()
        self.valuesFifo = valuesFifo
        self.samples = samples
        self.context = context
        self.variables = []
        self.positions = []
        self.currentTimeForces = 0
        self.currentTimeLocations = 0

        self.pkgTypesMap = {
              self.PKG_FORCE_VALUE: {'struct': self.ForceValue, 'handler': self.handleForce},
              self.PKG_LOCATION_VALUE: {'struct': self.LocationValue, 'handler': self.handleLocation},
              self.PKG_META_VARIABLE: {'struct': self.LocationMetaVariable, 'handler': self.handleMetaVariable},
              self.PKG_META_POSITION: {'struct': self.LocationMetaPosition, 'handler': self.handleMetaPosition}
            }

    def run(self):
        fifoOpened = True
        try:
            while fifoOpened and not self.context.errorsDetected:
                logging.debug("CollectorThread- Waiting for samples information...")
                pkgType = _readBlock(self.valuesFifo, 1)
                if pkgType is None:
                    fifoOpened = False
                else:
                    pkgTypeId = ord(pkgType)
                    logging.info("CollectorThread- Receiving package type: %d - %r" % (pkgTypeId, pkgType))
                    self._processPacket(pkgTypeId)
            logging.info('CollectorThread - Samples information FIFO closed. Finishing controller...')
        except Exception as e:
            logging.exception('CollectorThread - Closing with errors')
            self.context.errorsDetected = True

    def _processPacket(self, pkgTypeId):
        try:
            typeMap = self.pkgTypesMap[pkgTypeId]
            structType = typeMap['struct']
            handler = typeMap['handler']

            query = _readBlock(self.valuesFifo, structType.size)
            querySt = structType.unpack(query)
            handler(querySt)
        except KeyError:
                msg = 'Invalid struct type. Type=%d is not recognized as a valid package. Available types: %s'\
                       % (pkgTypeId, self.pkgTypesMap.keys())
                logging.error(msg)
                raise SyntaxError(msg)
        except struct.error as e:
            logging.error('Parsing error. Invalid struct data received. Data=%r', query)
            raise

    def handleForce(self, querySt):
        time = querySt[0]
        step = querySt[1]
        pf = (querySt[2],querySt[3],querySt[4])
        vf = (querySt[5],querySt[6],querySt[7])
        pm = (querySt[8],querySt[9],querySt[10])
        vm = (querySt[11],querySt[12],querySt[13])
        sample = Sample(time, step, ForceData(pf, vf, pm, vm))
        logging.debug("CollectorThread- Handling force value. step=%d - time=%.3f - pf=%s - ..."
                      % (step, time, pf))
        with self.context.lock:
            self.samples.addForce(sample)

    def handleLocation(self, querySt):
        time = querySt[0]
        step = querySt[1]
        variable = _normalizeKeyword(querySt[2])
        value = querySt[3]
        location = (querySt[4],querySt[5],querySt[6])
        sample = Sample(time, step, ProbeData(location, variable, value))
        logging.debug("CollectorThread- Handling location value. step=%d - time=%.3f - location=%s - variable=%s - value=%f"
                      % (step, time, location, variable, value))
        with self.context.lock:
            self.samples.addProbe(sample)

    def handleMetaPosition(self, querySt):
        with self.context.lock:
            self.currentTimeForces = 0
            self.currentTimeLocations = 0

        totalPositionsQty = querySt[0]
        position = (querySt[1], querySt[2], querySt[3])
        logging.debug("CollectorThread- Handling meta position. Position=(%.3f, %.3f, %.3f) - TotalPositions=%d" % (position[0], position[1], position[2], totalPositionsQty))
        if len(self.positions) < totalPositionsQty:
            self.positions.append(position)

    def handleMetaVariable(self, querySt):
        with self.context.lock:
            self.currentTimeForces = 0
            self.currentTimeLocations = 0

        totalVariablesQty = querySt[0]
        if len(self.variables) < totalVariablesQty:
            variable = _normalizeKeyword(querySt[1])
            self.variables.append(variable)
            
