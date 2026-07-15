import numpy as np
from scipy.constants import R

class Splitter:
    def __init__(self, R1, R2, R3):
        self.R1 = R1
        self.R2 = R2
        self.R3 = R3
        
    def split( self, time_array, volts_array, load_1_impedance, load_2_impedance, source_impedance ):
        
        branch_1_impedance = self.R2 + load_1_impedance
        branch_2_impedance = self.R3 + load_2_impedance
        
        parallel_impedance = (branch_1_impedance * branch_2_impedance) / (branch_1_impedance + branch_2_impedance)
        
        v_node = volts_array * (z_parallel / (source_impedance + self.R1 + parallel_impedance))
        
        v_out1 = v_node * (impedance_to_out1 / branch_1_impedance)
        v_out2 = v_node * (impedance_to_out2 / branch_2_impedance)
        
        return time_array, v_out1, v_out2

