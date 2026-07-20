import numpy as np


class Connector:

    @classmethod
    def connect(cls,
                time_array,
                open_circuit_voltage_array,
                source_impedance,
                load_impedance,
                signal_baseline=0.0):

        pulse_voltage = open_circuit_voltage_array - signal_baseline

        if np.isinf(load_impedance):
            load_factor = 1.0
        else:
            load_factor = load_impedance / ( source_impedance + load_impedance)
        
        loaded_voltage_array = ( signal_baseline + pulse_voltage * load_factor )

        return time_array, loaded_voltage_array