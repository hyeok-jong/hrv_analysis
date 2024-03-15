import numpy as np


def correct_rpeaks_pyhrv(rpeaks, sampling_rate):
    '''
    most of functions in pyhrv is coded based on 1000 Hz, and there are few function that have sampling_rate option.
    to this end, adjust rpeaks based on sampling_rate/1000 is best option.
    note that rpeaks is array consist of indices of r peaks.
    thus, if the signal sampled at 2000 Hz, the indices are doubled.
    '''
    rpeaks = np.array(rpeaks)
    ratio = sampling_rate / 1000
    corrected = rpeaks / ratio
    return corrected