import numpy as np


class Digitizer:
    """ Add event_threshold , polarity , pre_trigger_time , post_trigger_time later """
    
    def __init__(self, input_impedance=50.0):
        self.input_impedance = input_impedance

    @classmethod
    def digitize(cls, time_array: np.ndarray, voltage_array: np.ndarray, 
                 sampling_rate_Hz: float, num_bits: int, 
                 min_volts: float, max_volts: float, event_threshold: float = None,
                 polarity: int = None, pre_trigger_time: float = None,
                 post_trigger_time: float = None, dc_offset: float = 0 ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray ] :


        cls.validate_params(time_array, 
                            voltage_array, 
                            sampling_rate_Hz, 
                            num_bits,
                            event_threshold, 
                            polarity, 
                            pre_trigger_time, 
                            post_trigger_time,
                            min_volts,
                            max_volts
                            )        

        sample_period = 1 / sampling_rate_Hz
        
        t_0 = time_array[0]
        t_final = time_array[-1]
        
        num_periods = (t_final - t_0)/ sample_period
        num_periods = int(np.floor(np.nextafter(num_periods, np.inf)))

        discrete_times = t_0 + np.arange(num_periods + 1 ) * sample_period 
        #interpolation may not be the way - document this
        voltage_samples = cls.interpolate(time_array, voltage_array, discrete_times)
        
        voltage_samples = voltage_samples + dc_offset 

        was_clipped = (voltage_samples > max_volts) | (voltage_samples < min_volts) 
        clipped_voltage_samples = np.clip(voltage_samples, min_volts, max_volts)
        
        num_levels = 2 ** num_bits
        voltage_span = max_volts - min_volts
        least_significant_bit = voltage_span / num_levels
        
        #Floor being used for quantization - document this 
        Digitized_array = np.floor( (clipped_voltage_samples - min_volts) / least_significant_bit  )
        Digitized_array = np.clip(Digitized_array, 0, num_levels - 1,).astype(int)
        
        Reconstructed_array = min_volts + (Digitized_array + 1/2)*least_significant_bit
    
        return (discrete_times, Digitized_array, Reconstructed_array, was_clipped)
        
    @classmethod
    def validate_params(cls, time_array, voltage_array, sampling_rate_Hz, num_bits,event_threshold, polarity, pre_trigger_time, post_trigger_time, min_volts, max_volts):

        if max_volts - min_volts <= 0:
            raise ValueError("max_volts must be greater than min_volts")

        if len(time_array)!= len(voltage_array):
            raise ValueError("time_array and voltage_array must be of equal length")

        if len(time_array)!= len(voltage_array):
           raise ValueError("time_array and voltage_array must be of equal length")

        if sampling_rate_Hz <= 0 :
            raise ValueError("sampling rate must be positive")
        
        if(len(time_array) < 2):
            raise ValueError("time_array and voltage_array must contain at least 2 samples")
        
        if not np.all(np.isfinite(time_array)) or not np.all(np.isfinite(voltage_array)): 
            raise ValueError("time_array and voltage_array must contain only finite values")
        
        if num_bits < 0 or type(num_bits) is not int:
            raise ValueError("num_bits must be a positive integer")

        unimplemented = (event_threshold, polarity, pre_trigger_time, post_trigger_time)
        for param in unimplemented:
            if param is not None:  
                raise ValueError("Triggering not yet implemented")

    @classmethod
    def interpolate(cls, X, Y, val ):
        return np.interp(val, X, Y)