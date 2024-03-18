import pyhrv
import neurokit2 as nk
import numpy as np
from utils import correct_rpeaks_pyhrv


def pyhrv_nonlinear(rpeaks, sampling_rate, show = False):
    rpeaks = correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    result = pyhrv.nonlinear.poincare(rpeaks = rpeaks, show = False, mode = 'dev' if show == False else 'normal')
    result = dict(result)
    result['sd1/sd2'] = result['sd1'] / result['sd2']
    return dict(result)

def nk_nonlinear(rpeaks, sampling_rate):
    output = nk.hrv_nonlinear(rpeaks, sampling_rate)
    result = dict()
    for c in output.columns:
        result[c] = output[c].item()
    return dict(result)

def nonlinear(rpeaks, sampling_rate):
    result_dict = dict()
    result_dict['pyhrv nonlinear'] = pyhrv_nonlinear(rpeaks, sampling_rate)
    result_dict['nk nonlinear'] = nk_nonlinear(rpeaks, sampling_rate)
    return result_dict
    