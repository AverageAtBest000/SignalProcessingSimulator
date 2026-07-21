from signal import signal

import numpy as np
import matplotlib.pyplot as plt


class ConstantFractionDiscriminator:
    
    def __init__(self, attenuation:float = None, delay:float = None, armed_threshold:float = None):
        
        self.attenuation = attenuation
        self.delay = delay

    def apply(self, time_array: np.ndarray, open_circuit_voltage_array: np.ndarray, signal_baseline: float) -> tuple[np.ndarray, np.ndarray]:

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
            
            if(removed_baseline_array[i] > armed_treshold):
                armed = True
            else:
                armed = False
            
            if armed and (summed_array[i-1] < 0 and summed_array[i] >=0):
                crossing_time = np.interp(0, summed_array, time_array)
                
                np.append(crossing_times, crossing_time)
                np.append(cossing_indexes, i)


        return crossing_indexes, crossing_times
