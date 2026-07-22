import numpy as np

from ComponentClasses import Cable

class Terminator:
    
    def __init__(self, impedance: float):
        
        self.impedance = impedance


    def get_ref_coefficient(self, characteristic_impedance):

        if np.isinf(self.impedance):
            return 1.0
        
        return (self.impedance - characteristic_impedance) / (self.impedance + characteristic_impedance)

    def apply_reflection(self, 
                        cable: Cable, 
                        time_array: np.ndarray, 
                        open_circuit_voltage_array: np.ndarray, 
                        source_impedance: float,
                        signal_baseline: float, 
                        max_round_trips: float,
                        ) ->  tuple[np.ndarray, np.ndarray ] :

        return cable.propagation(
            time_array=time_array,
            open_circuit_voltage_array=open_circuit_voltage_array,
            source_impedance=source_impedance,
            load_impedance=self.impedance,
            signal_baseline=signal_baseline,
            max_round_trips=max_round_trips,
        )