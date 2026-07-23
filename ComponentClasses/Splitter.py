
"""Ideal resistor model- add cable delay, reflections, capacitance, etc. later on"""
import numpy as np

class Splitter:
    def __init__(self, R1, R2, R3):
        self.R1 = R1
        self.R2 = R2
        self.R3 = R3
        
    @classmethod 
    def get_parallel_impedance(cls, impedance_1, impedance_2):
        
        if np.isinf(impedance_1):
            return impedance_2
        if np.isinf(impedance_2):
            return impedance_1

        return(impedance_1*impedance_2/ (impedance_1 + impedance_2))
    

    @classmethod
    def voltage_divider( cls, open_circuit_voltage_array, series_impedance, load_impedance ):
        
        if np.isinf(load_impedance):
            return open_circuit_voltage_array

        return open_circuit_voltage_array * ( load_impedance / (series_impedance + load_impedance) )
    
    
    def split( self, time_array: np.ndarray, open_volts_array: np.ndarray, load_1_impedance: float, load_2_impedance: float, source_impedance: float, signal_baseline: float = 0.0 ) -> tuple[np.ndarray, np.ndarray, float, np.ndarray, float]:
        
        if len(time_array) != len(open_volts_array):
            raise ValueError("Time and Voltage array must be equal in length")

        pulse_voltage = open_volts_array  - signal_baseline
        #assume cable offers no imp.
        source_side_impedance =  source_impedance + self.R1

        branch_1_impedance = self.R2 + load_1_impedance
        branch_2_impedance = self.R3 + load_2_impedance
        
        open_circuit_output_1 = ( signal_baseline + self.voltage_divider( pulse_voltage, source_side_impedance, branch_2_impedance ) )
        output_impedance_1 = (self.R2 + self.get_parallel_impedance( source_side_impedance, branch_2_impedance) )

        open_circuit_output_2 = ( signal_baseline + self.voltage_divider( pulse_voltage, source_side_impedance, branch_1_impedance) )
        output_impedance_2 = ( self.R3 + self.get_parallel_impedance( source_side_impedance, branch_1_impedance ) )

        return ( time_array, open_circuit_output_1, output_impedance_1, open_circuit_output_2, output_impedance_2 )
