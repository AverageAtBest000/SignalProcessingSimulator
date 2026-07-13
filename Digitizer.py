
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

class Digitizer:
    
    @classmethod
    def digitize(cls, time_array, voltage_array, 
                 sampling_rate_seconds, num_bits, 
                 min_volts, max_volts, event_treshold, 
                 polarity, pre_trigger_time, post_trigger_time):
        
        sample_period = 1 / sampling_rate_seconds
        t_0 = time_array[0]
        t_final = time_array[len(time_array) - 1 ]
        
        discrete_times = np.linspace(t_0, t_final, (t_final - t_0)/sample_period)
        voltage_samples = np.zeros(len(discrete_times))
        
        for i in (len(discrete_times)):
            
            if np.any( time_array == discrete_times[i]):
                voltage_samples[i] = voltage_array[i]
            else:
                voltage_samples[i] = cls.interpolate(time_array, voltage_array, discrete_times[i])
                
        clipped_array  = np.clip(voltage_array, min_volts, max_volts)
        clipped = np.array_equal(voltage_array, clipped_array)
        
        voltage_span = max_volts - min_volts
        least_significant_bit = (voltage_span) / ( 2 ** num_bits)
        
        #Floor being used for quantization - document this 
        
        Digitized = np.floor( (clipped - min_volts) / least_significant_bit  )

    @classmethod
    def interpolate(cls, X, Y, val ) -> float :
        return np.interp(val, X, Y)