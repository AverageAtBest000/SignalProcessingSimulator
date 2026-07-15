
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import value
import scipy.stats as stats

class Digitizer:
    """ Add event_threshold , polarity , pre_trigger_time , post_trigger_time later """
    @classmethod
    def digitize(cls, time_array, voltage_array, 
                 sampling_rate_Hz, num_bits, 
                 min_volts, max_volts):
    
        sample_period = 1 / sampling_rate_Hz
        t_0 = time_array[0]
        t_final = time_array[len(time_array) - 1 ]
        
        discrete_times = np.linspace(t_0, t_final, (t_final - t_0)/sample_period)
        voltage_samples = cls.interpolate(time_array, voltage_array, discrete_times)
        
        clipped_voltage_samples = np.clip(voltage_samples, min_volts, max_volts)
        was_clipped = (voltage_samples > max_volts) or (voltage_samples <= min_volts) 

        voltage_span = max_volts - min_volts
        least_significant_bit = (voltage_span) / ( 2 ** num_bits - 1)
        
        #Floor being used for quantization - document this 
        Digitized_array = int(np.floor( (clipped_voltage_samples - min_volts) / least_significant_bit  ))
        Reconstructed_array = min_volts + (Digitized_array + 1/2)*least_significant_bit
        
        
        return discrete_times, Digitized_array, Reconstructed_array, was_clipped
        
        
    @classmethod
    def interpolate(cls, X, Y, val ) -> float :
        return np.interp(val, X, Y)