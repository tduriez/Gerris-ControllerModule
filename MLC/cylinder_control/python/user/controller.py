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
        act = ((S1 - (tanh(((tanh((34.69 - (((tanh(tanh((51.52 - (-53.11)))) + (tanh(tanh(S7)) * (tanh(S2) - (-56.68)))) + (-84.4)) - (tanh(tanh(((S1 + (-57.45)) - S6))) - tanh((-39.46)))))) * (((tanh(tanh(S4)) + (S5 * (85.21 - (-84.86)))) * S4) * tanh((tanh((S4 + (-5.752))) * tanh(tanh(((88.45 - (S3 * 46.26)) * S2))))))) + tanh((6.12 * (-32.03))))) + (tanh(((((tanh(((-96.27) - tanh(tanh(S1)))) * tanh((tanh(55.99) - ((-88.29) - ((S6 + (-3.725)) + tanh((-24.12))))))) * tanh(29.92)) - ((36.2 * ((48.87 - (-42.95)) - tanh((S2 + ((85.21 - (-84.86)) - 35.41))))) - 82.06)) - (((-64.13) + (tanh(((S3 * 10.32) - ((tanh(S4) + ((-26.76) - (-93.62))) - ((65.21 * S7) + (S4 - 15.25))))) - tanh((tanh(tanh(S4)) + (S3 - (((-42.05) - S1) - ((-47.89) * (-52.36)))))))) + ((72.51 * S3) + (-35.16))))) + ((-73.31) - 55.99)))) * tanh(tanh(S2)))
        if act < 0:
                act=0
        if act > 20.000000:
                act=20.000000
        logging.info('** fixed actuation ** step=%d - t=%.3f - act=%.2f **' % (step, completed_time, act))
    return act
