from math import *
import logging
import ConfigParser
import numpy as np
import math
import csv
import os, os.path
import time

def custom_filter_inputs(all_samples):
    values = [s.data.value for s in all_samples
                           if s.data.variable == 'T' and s.data.location == (3, 1, 0) and s.time > 60.0
             ]
    return values

def init(proc_index):
    pass

def destroy(proc_index):
    pass

def actuation(time, step, samples):
    act = 0
    completed_time = samples.getPreviousClosestTime(time)
    if completed_time:
        filtered_samples = samples.samplesByTime(completed_time)
        filtered_samples = samples.samplesByVariable('T')
        filtered_samples = samples.samplesByLocation( (3,1,0) )
        filtered_samples = custom_filter_inputs(samples.all)
        act = 5
        logging.info('** fixed actuation ** step=%d - t=%.3f - act=%.2f **' % (step, completed_time, act))
    return act

