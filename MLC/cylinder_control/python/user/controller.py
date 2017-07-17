from math import *
import logging
import ConfigParser
import numpy as np
import math
import csv
import os, os.path
import time

def init(proc_index):
    pass

def destroy(proc_index):
    pass

def actuation(time, step, samples):
    act = 0
    completed_time = samples.completedTime
    if completed_time:
        S = samples.search().byTime(completed_time).byVariable('T').asValues()
        S0 = S[0]
        S1 = S[1]
        S2 = S[2]
        S3 = S[3]
        S4 = S[4]
        S5 = S[5]
        S6 = S[6]
        S7 = S[7]
        act = (((S5 * 86.47) - (S3 * (-59.31))) + tanh((S4 * (-47.39))))
        if act < 0:
                act=0
        if act > 20.000000:
                act=20.000000
        logging.info('** fixed actuation ** step=%d - t=%.3f - act=%.2f **' % (step, completed_time, act))
    return act
