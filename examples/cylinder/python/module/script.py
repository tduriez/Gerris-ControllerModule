from math import *
import logging

actuationStartTime = 40.
velocityRef = 1.
kProp = 0.55
kInt = 0.3

def strLocations(locList):
    out = []
    for loc in locList:
        out.append('step=%d-t=%.3f-' % (loc.step, loc.time))
        for var in loc.data.getVariables():
            out.append(var)
            out.append("=[")
            for posValue in loc.data.getValues(var):
                pos,value = posValue
                out.append('%.3f ' % value)
            out.append("]")
        out.append(" ")
    return ' '.join(out)

def velocityAbsErrorIntegrate(velocityRef, locations):
    integral = 0;
    for loc in locations:
        integral += velocityAbsError(velocityRef, loc)
    return integral

def velocityAbsError(velocityRef, loc):
    error = 0
    uList = loc.data.getValues('U')
    vList = loc.data.getValues('V')
    for i in range(len(uList)):
        u = uList[i][1]
        v = vList[i][1]
        absError = abs(sqrt(u*u + v*v) - velocityRef)
        error += absError
    return error

def actuation(forces,locations):
    global velocityRef, kProp, kInt, actuationStartTime
    act = 0.
    if len(locations) > 0:
        lastSamples = locations[-1]
        step=lastSamples.step
        time=lastSamples.time
        if time >= actuationStartTime:
            act = kProp*velocityAbsError(velocityRef, lastSamples) + kInt*velocityAbsErrorIntegrate(velocityRef, locations)
        logging.info('step=%d - t=%.3f - act=%.2f - e=%.2f - eInt=%.2f' % (step, time, act, velocityAbsError(velocityRef, lastSamples),velocityAbsErrorIntegrate(velocityRef, locations)))
        logging.info('step=%d - t=%.3f - act=%.2f' % (step, time, act))
    return act

