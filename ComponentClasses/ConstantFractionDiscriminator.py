import numpy as np
import matplotlib.pyplot as plt


class ConstantFractionDiscriminator:
    
    def __init__(self, attenuation:float = None, delay:float = None):
        
        self.attenuation = attenuation
        self.delay = delay

    def apply(self, time_array: np.ndarray, open_circuit_voltage_array: np.ndarray) -> tuple[np.ndarray, np.ndarray]:


        attenuated_array = open_circuit_voltage_array * self.attenuation
        attenuated_array = attenuated_array * -1


        delayed_time_array = time_array - delay
        delayed_time_array = np.clip(delayed_array, 0, max = None)
        
        delayed_voltage_array = np.interp(delayed_time_array, time_array, open_circuit_voltage_array)


        summed_array = delayed_voltage_array + attenuated_array

        
    

