from math import *
import logging
import ConfigParser
import numpy as np
import math
import csv
import os, os.path
import time

def custom_filter_inputs(all_samples,completed_time):
    values = [s.data.value for s in all_samples
                           if s.data.variable == 'T' and s.time == completed_time
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
        S = S = custom_filter_inputs(samples.all,completed_time)
        S0 = S[0]
        S1 = S[1]
        S2 = S[2]
        S3 = S[3]
        S4 = S[4]
        S5 = S[5]
        S6 = S[6]
        S7 = S[7]
        act = (S3 * 0.4035)
        if act < 0:
                act=0
        if act > 5.000000:
                act=5.000000
        logging.info('** fixed actuation ** step=%d - t=%.3f - act=%.2f **' % (step, completed_time, act))
    return act
