import logging
import numpy as np
actuation_start_time=40.
actuation_end_time=42.
actuation_velocity=10.

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

def actuation(forcesList,locList):
	global actuation_start_time
	global actuation_end_time
	if len(forcesList) > 0:
		act = 0.
		step=forcesList[-1].step
		time=forcesList[-1].time
		if time >= actuation_start_time and time <= actuation_end_time:
			act = actuation_velocity
		logging.info('step=%d - t=%.3f - act=%.2f' % (step, time, act))
		logging.debug('Locations[%d]... %s' % (len(locList), strLocations(locList)))
		return act
	else:
		return 0.

