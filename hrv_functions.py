import pyhrv
import neurokit2 as nk
import biosppy
import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt



print(f'pyhrv version : {pyhrv.__version__}')
print(f'biosppy version : {biosppy.__version__}')
print(f'nk version : {nk.__version__}')


def peak_detection(signal, peak_method, sampling_rate, show = False, with_filtered = False):
    
    if peak_method == 'biosppy':
        if with_filtered:
            filtered, rpeaks = biosppy.signals.ecg.ecg(signal, sampling_rate = sampling_rate, show = show)[1:3]
        else:
            rpeaks = biosppy.signals.ecg.ecg(signal, sampling_rate = sampling_rate, show = show)['rpeaks']
        
    elif peak_method == 'nk':
        temp = nk.ecg_process(signal, sampling_rate = sampling_rate)[0][['ECG_R_Peaks', 'ECG_Clean']]
        rpeaks = temp[temp['ECG_R_Peaks'] == 1].index
        rpeaks = list(rpeaks)
        if with_filtered:
            filtered = temp['ECG_Clean'].tolist()
    
    if with_filtered:
        return rpeaks, filtered
    else:
        return rpeaks


def time_domain(signal, peak_method, method, sampling_rate):
    assert peak_method in ['nk', 'biosppy']
    assert method in ['nk', 'pyhrv']
    assert type(sampling_rate) == int
    
    if method == 'pyhrv' and sampling_rate != 1000: print(f'Warning : Case for pyhrv with not 1000Hz, RR intervals should be adjusted.')
    
    rpeaks = peak_detection(signal, peak_method, sampling_rate)
    
    if method == 'pyhrv':
        result = pyhrv.time_domain.time_domain(rpeaks = rpeaks, show = False, plot = False)
        result = dict(result)
        result = {key : result[key] for key in ['hr_mean', 'sdnn', 'rmssd', 'pnn50']}
        
    elif method == 'nk':
        # https://neuropsychology.github.io/NeuroKit/functions/hrv.html#neurokit2.hrv.hrv_time
        result = nk.hrv_time(peaks = rpeaks, sampling_rate = sampling_rate, show = False)[['HRV_SDNN', 'HRV_RMSSD', 'HRV_pNN50']]
        result.rename({'HRV_SDNN' : 'sdnn', 'HRV_RMSSD' : 'rmssd', 'HRV_pNN50' : 'pnn50'}, inplace = True, axis = 1)
        result = result.to_dict()
        result = {key : val[0] for key, val in result.items()}
        
    return result


def frequency_domain(signal, peak_method, method, sampling_rate, plotting = False):
    if plotting: 
        plt.ion()
    else:
        plt.ioff()
        
    assert peak_method in ['nk', 'biosppy']
    assert method in ['nk', 'pyhrv']
    assert type(sampling_rate) == int
    
    if method == 'pyhrv' and sampling_rate != 1000: print(f'Warning : Case for pyhrv with not 1000Hz, RR intervals should be adjusted.')
    
    rpeaks = peak_detection(signal, peak_method, sampling_rate)
        
    if method == 'pyhrv':
        result = pyhrv.frequency_domain.frequency_domain(
            rpeaks = rpeaks, 
            sampling_rate = sampling_rate, 
            show = False, 
            show_param = False, 
            legend = True,
        )
        
        result = {key : result[key] for key in ['fft_ratio', 'lomb_ratio', 'ar_ratio']}
        
    elif method == 'nk':
        # https://neuropsychology.github.io/NeuroKit/functions/signal.html#neurokit2.signal_power
        result = dict()
        
        welch = nk.hrv_frequency(rpeaks, sampling_rate, psd_method = 'welch')
        result['welch'] = float(welch['HRV_LF'] / welch['HRV_HF'])
        
        fft = nk.hrv_frequency(rpeaks, sampling_rate, psd_method = 'fft')
        result['fft'] = float(fft['HRV_LF'] / fft['HRV_HF'])
        
        lombscargle = nk.hrv_frequency(rpeaks, sampling_rate, psd_method = 'lombscargle')
        result['lombscargle'] = float(lombscargle['HRV_LF'] / lombscargle['HRV_HF'])
        
    
    return result
    
    
    
def non_linear(signal, peak_method, method, sampling_rate, plotting = False):
    if plotting: 
        plt.ion()
    else:
        plt.ioff()
        
    assert peak_method in ['nk', 'biosppy']
    assert method in ['nk', 'pyhrv']
    assert type(sampling_rate) == int
    
    if method == 'pyhrv' and sampling_rate != 1000: print(f'Warning : Case for pyhrv with not 1000Hz, RR intervals should be adjusted.')
    
    rpeaks = peak_detection(signal, peak_method, sampling_rate)
        
    if method == 'pyhrv':
        result_ = pyhrv.nonlinear.nonlinear(
            rpeaks = rpeaks, 
            sampling_rate = sampling_rate, 
            show = False, 
        )
        
        result = {'sd1_sd2' : result_['sd_ratio']}
        
    elif method == 'nk':
        # https://neuropsychology.github.io/NeuroKit/functions/hrv.html#neurokit2.hrv.hrv_nonlinear
        result = dict()
        result_ = nk.hrv_nonlinear(rpeaks, sampling_rate, show = False)
        result['sd1_sd2'] = float(result_['HRV_SD1SD2'])
        
    
    return result
    
    