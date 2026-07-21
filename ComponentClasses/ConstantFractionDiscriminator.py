import numpy as np
import matplotlib.pyplot as plt


class ConstantFractionDiscriminator:
    
    def __init__(self, attenuation:float = None, delay:float = None, armed_threshold:float = None):
        
        self.attenuation = attenuation
        self.delay = delay
        self.armed_threshold = armed_threshold

    def apply(self, time_array: np.ndarray, open_circuit_voltage_array: np.ndarray, signal_baseline: float, polarity:float) -> tuple[np.ndarray, np.ndarray]:

        removed_baseline_array  = open_circuit_voltage_array - signal_baseline

        attenuated_array = removed_baseline_array * self.attenuation
        attenuated_array = attenuated_array * -1


        delayed_time_array = time_array - self.delay
        # delayed_time_array = np.clip(delayed_time_array, signal_baseline, max = None)
        negative_time_indexes = np.where(delayed_time_array < 0)[0]

        delayed_voltage_array = np.interp(delayed_time_array, time_array, removed_baseline_array)
        delayed_voltage_array[negative_time_indexes] = signal_baseline

        summed_array = delayed_voltage_array + attenuated_array

        crossing_times = np.array([])
        crossing_indexes = np.array([])
        
        armed = False
        
        for i in range(len(summed_array)):
            
            if (not armed) and (self.is_over_armed_threshold(polarity, self.armed_threshold, summed_array[i])):
                armed = True
            
            if armed and self.has_crossed(polarity, summed_array[i-1], summed_array[i-1]):
                
                time_list = np.array([time_array[i-1], time_array[1]])
                voltage_list = np.array([summed_array[i-1], summed_array[1]])

                crossing_time = np.interp(0, voltage_list, time_list)
                
                crossing_times = np.append(crossing_times, crossing_time)
                crossing_indexes =  np.append(crossing_indexes, i)

                armed = False


        return crossing_indexes, crossing_times

    
    def has_crossed(self, polarity, num1, num2):

        if polarity == -1 and (num1 < 0 and num2 >=0):
            return True
        elif polarity == 1 and (num1 >= 0 and num2 < 0):
            return True

        return False

    
    def is_over_armed_threshold(self, polarity, armed_threshold, num):
        
        
        if(polarity == -1):
            if(num >= armed_threshold):
                return True
        else:
            if(num <= -armed_threshold):
                return True

        return False

