# version : 2024.06.10

import neurokit2 as nk
import numpy as np
import pyhrv

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



def nk_filter(signal, sampling_rate = 200):
    signal = nk.signal_sanitize(signal)
    filtered = nk.ecg_clean(
        ecg_signal = signal,
        sampling_rate = sampling_rate,
        method = 'neurokit'
    )
    return {'filtered' : filtered}

def nk_rpeaks(filtered, sampling_rate = 200):
    temp, info = nk.ecg_peaks(
        filtered,
        sampling_rate
    )
    rpeaks = temp[temp['ECG_R_Peaks'] == 1].index
    rpeaks = list(rpeaks)
    return {'rpeaks' : rpeaks}






def pyhrv_hr(rpeaks, sampling_rate):
    # https://github.com/PGomes92/pyhrv/blob/73ea446ecf7d3416fef86fc4025ddcc242398e3f/pyhrv/time_domain.py#L311
    rpeaks = correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    nn = pyhrv.utils.check_input(nni = None, rpeaks = rpeaks)
    hr = pyhrv.tools.heart_rate(nn)
    return {'hr' : hr.mean()}

def pyhrv_rmssd(rpeaks, sampling_rate):
    # https://github.com/PGomes92/pyhrv/blob/73ea446ecf7d3416fef86fc4025ddcc242398e3f/pyhrv/time_domain.py#L311
    rpeaks = correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    nn = pyhrv.utils.check_input(nni = None, rpeaks = rpeaks)
    nnd = pyhrv.tools.nni_diff(nn)
    rmssd_ = np.sum([x**2 for x in nnd])
    rmssd = np.sqrt(1. / nnd.size * rmssd_)

    return {'rmssd' : rmssd}

def pyhrv_sdnn(rpeaks, sampling_rate):
    # https://github.com/PGomes92/pyhrv/blob/73ea446ecf7d3416fef86fc4025ddcc242398e3f/pyhrv/time_domain.py#L173
    rpeaks = correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    nn = pyhrv.utils.check_input(nni = None, rpeaks = rpeaks)
    sdnn = pyhrv.utils.std(nn)
    return {'sdnn' : sdnn}

def pyhrv_time(rpeaks, sampling_rate = 200):
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




def pyhrv_nonlinear(rpeaks, sampling_rate = 200, show = False):
    rpeaks = correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    result = pyhrv.nonlinear.poincare(rpeaks = rpeaks, show = False, mode = 'dev' if show == False else 'normal')
    result = dict(result)
    return result['sd1'] / result['sd2']




def pyhrv_welch(rpeaks, sampling_rate = 200, show = False):
    rpeaks = correct_rpeaks_pyhrv(rpeaks, sampling_rate)
    result = pyhrv.frequency_domain.welch_psd(rpeaks = rpeaks, show = False, mode = 'dev' if show == False else 'normal')
    return dict(result[0])['fft_ratio']



def processECG(data):
    ecg_signal = data['ecgArray']
    
    try:
        filtered = nk_filter(ecg_signal)['filtered']
    except:
        return { "HR" : 'None', 'ECG_Processed' : 'None', 'RMSSD' : None, 'SDNN' : None, 'SD1_SD2'  : None, 'LF_HF' : None,
                'Short_Message' : 'ECG_Filtering_Error'}
    
    try:
        peaks = nk_rpeaks(filtered)['rpeaks']
    except:
        return { "HR" : 'None', 'ECG_Processed' : 'None', 'RMSSD' : None, 'SDNN' : None, 'SD1_SD2'  : None, 'LF_HF' : None,
                'Short_Message' : 'ECG_Detecting_Peaks_Error'}
        
    short_error = ''
    
    try:
        time_results = pyhrv_time(peaks)
        HR = time_results['pyhrv hr']
        RMSSD = time_results['pyhrv rmssd']
        SDNN = time_results['pyhrv sdnn']
        
    except:
        HR, RMSSD, SDNN = None, None, None
        short_error += 'ECG_Time_Error, '
        
    
    try:
        SD1_SD2 = pyhrv_nonlinear(peaks)
        
    except:
        SD1_SD2 = None
        short_error += 'ECG_Nonlinear_Error, '
        
        
        
    try:
        LF_HF = pyhrv_welch(peaks)
        
    except:
        LF_HF = None
        short_error += 'ECG_Nonlinear_Error, '
        
    return { "HR" : HR, 'ECG_Processed' : filtered, 'RMSSD' : RMSSD, 'SDNN' : SDNN, 'SD1_SD2'  : SD1_SD2, 'LF_HF' : LF_HF,
                'Short_Message' : 'SUCCESS'}
        
    
    