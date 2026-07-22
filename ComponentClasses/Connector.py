import numpy as np


class Connector:

    @classmethod
    def connect(cls,
                time_array: np.ndarray,
                open_circuit_voltage_array: np.ndarray,
                source_impedance: float,
                load_impedance: float,
                signal_baseline:float = 0.0) -> tuple[np.ndarray, np.ndarray]:

        pulse_voltage = open_circuit_voltage_array - signal_baseline

        if np.isinf(load_impedance):
            load_factor = 1.0
        else:
            load_factor = load_impedance / ( source_impedance + load_impedance)
        
        loaded_voltage_array = ( signal_baseline + pulse_voltage * load_factor )

        return time_array, loaded_voltage_array