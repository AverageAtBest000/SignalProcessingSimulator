
"""Ideal resistor model- add cable delay, reflections, capacitance, etc. later on"""
class Splitter:
    def __init__(self, R1, R2, R3):
        self.R1 = R1
        self.R2 = R2
        self.R3 = R3
        
    def split( self, time_array, volts_array, load_1_impedance, load_2_impedance, source_impedance, signal_baseline = 0.0 ):
        if len(time_array) != len(volts_array):
            raise ValueError("Time and Voltage array must be equal in length")

        pulse_voltage = volts_array - signal_baseline
            
        branch_1_impedance = self.R2 + load_1_impedance
        branch_2_impedance = self.R3 + load_2_impedance
        
        parallel_impedance = (branch_1_impedance * branch_2_impedance) / (branch_1_impedance + branch_2_impedance)
        
        v_node = pulse_voltage * (parallel_impedance / (source_impedance + self.R1 + parallel_impedance))
        
        v_out1 = signal_baseline + v_node * (load_1_impedance / branch_1_impedance)
        v_out2 = signal_baseline + v_node * (load_2_impedance / branch_2_impedance)
        
        return time_array, v_out1, v_out2
