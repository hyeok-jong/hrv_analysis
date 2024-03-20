import pyhrv
import neurokit2 as nk
import numpy as np
from utils import correct_rpeaks_pyhrv


def pyhrv_welch(rpeaks, sampling_rate, show = False):
    rpeaks = correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    result = pyhrv.frequency_domain.welch_psd(rpeaks = rpeaks, show = False, mode = 'dev' if show == False else 'normal')
    return dict(result[0])

def pyhrv_ar(rpeaks, sampling_rate, show = False):
    rpeaks = correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    result = pyhrv.frequency_domain.ar_psd(rpeaks = rpeaks, show = False, mode = 'dev' if show == False else 'normal')
    result = dict(result[0])
    result['ar_ratio'] = 1/result['ar_ratio']
    return result


def pyhrv_frequency(rpeaks, sampling_rate, show = False):
    result = dict()
    result.update({
        'pyhrv welch' : pyhrv_welch(rpeaks, sampling_rate, show),
        'pyhrv ar' : pyhrv_ar(rpeaks, sampling_rate, show),
    })
    return result


def nk_welch(rpeaks, sampling_rate):
    output = nk.hrv_frequency(peaks = rpeaks, sampling_rate = sampling_rate, psd_method = 'welch')
    result = dict()
    for c in output.columns:
        result[c] = output[c].item()
    return result

def nk_fft(rpeaks, sampling_rate):
    output = nk.hrv_frequency(peaks = rpeaks, sampling_rate = sampling_rate, psd_method = 'fft')
    result = dict()
    for c in output.columns:
        result[c] = output[c].item()
    return result

def nk_frequency(rpeaks, sampling_rate):
    result = dict()
    result.update({
        'nk welch' : nk_welch(rpeaks, sampling_rate),
        'nk fft' : nk_fft(rpeaks, sampling_rate),
    })
    return result
    
def frequency(rpeaks, sampling_rate):
    result = dict()
    result.update(pyhrv_frequency(rpeaks, sampling_rate))
    result.update(nk_frequency(rpeaks, sampling_rate))
    return result