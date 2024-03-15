import pyhrv, biosppy
import neurokit2 as nk
import numpy as np
from utils import correct_rpeaks_pyhrv

def biosppy_hr(rpeaks, sampling_rate):
    sampling_rate = float(sampling_rate)
    hr_idx, hr = biosppy.signals.tools.get_heart_rate(
    beats = rpeaks, 
    sampling_rate = sampling_rate, 
    smooth = True, 
    size = 3
    )
    return {'hr' : hr}


def pyhrv_hr(rpeaks, sampling_rate):
    # https://github.com/PGomes92/pyhrv/blob/73ea446ecf7d3416fef86fc4025ddcc242398e3f/pyhrv/time_domain.py#L311
    rpeaks =correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    nn = pyhrv.utils.check_input(nni = None, rpeaks = rpeaks)
    hr = pyhrv.tools.heart_rate(nn)
    return {'hr' : hr.mean()}

def pyhrv_rmssd(rpeaks, sampling_rate):
    # https://github.com/PGomes92/pyhrv/blob/73ea446ecf7d3416fef86fc4025ddcc242398e3f/pyhrv/time_domain.py#L311
    rpeaks =correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    nn = pyhrv.utils.check_input(nni = None, rpeaks = rpeaks)
    nnd = pyhrv.tools.nni_diff(nn)
    rmssd_ = np.sum([x**2 for x in nnd])
    rmssd = np.sqrt(1. / nnd.size * rmssd_)

    return {'rmssd' : rmssd}

def pyhrv_sdnn(rpeaks, sampling_rate):
    # https://github.com/PGomes92/pyhrv/blob/73ea446ecf7d3416fef86fc4025ddcc242398e3f/pyhrv/time_domain.py#L173
    rpeaks =correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    nn = pyhrv.utils.check_input(nni = None, rpeaks = rpeaks)
    sdnn = pyhrv.utils.std(nn)
    return {'sdnn' : sdnn}

def pyhrv_time(rpeaks, sampling_rate):
    result = dict()

    result.update({
        'pyhrv hr' : pyhrv_hr(rpeaks, sampling_rate)['hr']
    })
    result.update({
        'pyhrv rmssd' : pyhrv_rmssd(rpeaks, sampling_rate)['rmssd']
    })
    result.update({
        'pyhrv sdnn' : pyhrv_sdnn(rpeaks, sampling_rate)['sdnn']
    })
    return result


def nk_time(rpeaks, sampling_rate):
    # just for test
    out = nk.hrv_time(rpeaks, sampling_rate, False)
    return {
        'nk rmssd' : float(out['HRV_RMSSD']),
        'nk sdnn' : float(out['HRV_SDNN'])
    }
    
def time(rpeaks, sampling_rate):
    result = dict()
    result.update(pyhrv_time(rpeaks, sampling_rate))
    result.update(nk_time(rpeaks, sampling_rate))
    result.update({
        'biosspy hr' : biosppy_hr(rpeaks, sampling_rate)['hr'].mean()
    })
    return result



























































