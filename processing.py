import numpy as np
import biosppy
import neurokit2 as nk

'''
Note that, R-peaks alone have no information about the sampling_rate
'''

def biosppy_filter(signal, sampling_rate):
    signal = np.array(signal)
    sampling_rate = float(sampling_rate)
    filtered, _, _ = biosppy.signals.tools.filter_signal(
        signal = signal, 
        ftype = 'FIR', 
        band = 'bandpass', 
        order = int(0.3 * sampling_rate), 
        frequency = [3, 45], 
        sampling_rate = sampling_rate)
    return {'filtered' : filtered}


def biosppy_rpeaks(filtered, sampling_rate):
    sampling_rate = float(sampling_rate)
    (rpeaks,) = biosppy.signals.ecg.hamilton_segmenter(
        signal = filtered, 
        sampling_rate = sampling_rate
        )

    (rpeaks,) = biosppy.signals.ecg.correct_rpeaks(
        signal = filtered, 
        rpeaks = rpeaks, 
        sampling_rate = sampling_rate, 
        tol=0.05
        )

    templates, rpeaks = biosppy.signals.ecg.extract_heartbeats(
        signal = filtered,
        rpeaks = rpeaks,
        sampling_rate = sampling_rate,
        before = 0.2,
        after= 0.4,
        )
    return {'rpeaks' : rpeaks}


def biosppy_processing(signal, sampling_rate):
    filtered = biosppy_filter(signal, sampling_rate)['filtered']
    rpeaks = biosppy_rpeaks(filtered, sampling_rate)['rpeaks']
    return {'filtered' : filtered, 'rpeaks' : np.array(rpeaks)}


def nk_filter(signal, sampling_rate):
    signal = nk.signal_sanitize(signal)
    filtered = nk.ecg_clean(
        ecg_signal = signal,
        sampling_rate = sampling_rate,
        method = 'neurokit'
    )
    return {'filtered' : filtered}

def nk_rpeaks(filtered, sampling_rate):
    temp, info = nk.ecg_peaks(
        filtered,
        sampling_rate
    )
    rpeaks = temp[temp['ECG_R_Peaks'] == 1].index
    rpeaks = list(rpeaks)
    return {'rpeaks' : rpeaks}

def nk_processing(signal, sampling_rate):
    filtered = nk_filter(signal, sampling_rate)['filtered']
    rpeaks = nk_rpeaks(signal, sampling_rate)['rpeaks']
    return {'filtered' : filtered, 'rpeaks' : np.array(rpeaks)}
    
    
def processing_aggregate(signal, sampling_rate):
    nk_result = nk_processing(signal, sampling_rate)
    biosppy_result = biosppy_processing(signal, sampling_rate)
    if nk_result['rpeaks'][0] - biosppy_result['rpeaks'][0] > sampling_rate // 4 :
        rpeaks = [biosppy_result['rpeaks'][0]] + list(nk_result['rpeaks'])
    else: rpeaks = nk_result['rpeaks']
    return {
        'rpeaks' : np.array(rpeaks),
        'nk filtered' : nk_result['filtered'],
        'biosppy filtered' : biosppy_result['filtered'],
    }
    
    


