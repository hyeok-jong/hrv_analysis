
# 원래 함수인데 지우지 말것
# github test branch에 있던것이다.
def processECG(data): 
    
    
    ecg_signal = data['ecgArray']
    
    try:
        _, info = nk.ecg_process(ecg_signal, sampling_rate = 200)
        rpeaks = info["ECG_R_Peaks"]
        hrv_indices_time = nk.hrv_time(rpeaks, sampling_rate = 200)
        meannn = hrv_indices_time["HRV_MeanNN"][0]
        pnn50 = hrv_indices_time["HRV_pNN50"][0]
        test_HRV = meannn, pnn50
    except:
        test_HRV = 'None', 'None'
    
    sampling_rate = 200  
    method = 'neurokit'
    
    try:
        ecg_signal = nk.signal_sanitize(ecg_signal)
        ecg_cleaned = nk.ecg_clean(ecg_signal, sampling_rate = sampling_rate, method = method)
    except Exception as e:
        return { "HR": 'None', 'ECG_Processed' : 'None', 'ECG_MeanNN' : test_HRV[0], 'ECG_pNN50' : test_HRV[1], 
                'Short_Message' : 'ECG_Filtering_Error'}
    
    # Detect R-peaks
    try:
        _, info = nk.ecg_peaks(
            ecg_cleaned = ecg_cleaned,
            sampling_rate = sampling_rate,
            method = method,
            correct_artifacts = True,
        )
    except Exception as e:
        return { "HR": 'None', 'ECG_Processed' : list(ecg_cleaned), 'ECG_MeanNN' : test_HRV[0], 'ECG_pNN50' : test_HRV[1], 
                'Short_Message' : 'ECG_Detecting_Peaks_Error'}
    
    # Calculate Heart Rate
    try:    
        rate = nk.signal_rate(
            info, sampling_rate=sampling_rate, desired_length=len(ecg_cleaned)
        )
        rate = rate.mean()
        
        rate = round(rate, 1)
        
    except Exception as e:
        return { "HR": 'None', 'ECG_Processed' : list(ecg_cleaned), 'ECG_MeanNN' : test_HRV[0], 'ECG_pNN50' : test_HRV[1], 
                'Short_Message' : 'ECG_Computing_HeartRate_Error'}
    
    if np.isnan(rate):
        return { "HR": 'None', 'ECG_Processed' : list(ecg_cleaned), 'ECG_MeanNN' : test_HRV[0], 'ECG_pNN50' : test_HRV[1], 
                'Short_Message' : 'ECG_Computing_HeartRate_Error'}
        
    return { "HR": rate, 'ECG_Processed' : list(ecg_cleaned), 'ECG_MeanNN' : test_HRV[0], 'ECG_pNN50' : test_HRV[1],
            'Short_Message' : 'SUCCESS'}