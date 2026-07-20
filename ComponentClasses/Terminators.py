import numpy as np

class Terminator:
    
    def __init__(self, impedance):
        
        self.impedance = impedance


    def get_ref_coefficient(self, characteristic_impedance):

        if np.isinf(self.impedance):
            return 1.0
        
        return (self.impedance - characteristic_impedance) / (self.impedance + characteristic_impedance)

    def apply_reflection(self, 
                        cable, 
                        time_array, 
                        voltage_array, 
                        source_impedance,
                        signal_baseline, 
                        max_round_trips,
                        ):

        return cable.propagation(
            time_array=time_array,
            voltage_array=voltage_array,
            source_impedance=source_impedance,
            load_impedance=self.impedance,
            signal_baseline=signal_baseline,
            max_round_trips=max_round_trips,
        )