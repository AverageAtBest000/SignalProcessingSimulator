
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
        
        for i in range(len(discrete_times)):
            
            if np.any( time_array == discrete_times[i]):
                voltage_samples[i] = voltage_array[time_array == discrete_times[i]][0]           
            else:
                voltage_samples[i] = cls.interpolate(time_array, voltage_array, discrete_times[i])
                
        clipped_voltage_samples = np.clip(voltage_samples, min_volts, max_volts)
        was_clipped = np.array_equal(voltage_samples, clipped_voltage_samples)
        
        voltage_span = max_volts - min_volts
        least_significant_bit = (voltage_span) / ( 2 ** num_bits)
        
        
        #Floor being used for quantization - document this 
        Digitized_array = np.floor( (clipped_voltage_samples - min_volts) / least_significant_bit  )
        Reconstructed_array = min_volts + (Digitized_array + 1/2)*least_significant_bit
        
        
        return Digitized_array, Reconstructed_array, was_clipped
        
        
    @classmethod
    def interpolate(cls, X, Y, val ) -> float :
        return np.interp(val, X, Y)