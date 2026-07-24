
"""Ideal resistor model- add cable delay, reflections, capacitance, etc. later on"""
import numpy as np

class Splitter:
    def __init__(self, R1:float, R2:float, R3:float):
        """
        Stored the resistor values for the three resistor splitter

        Args:
            R1 (float): Resistance value in Ohms of the first resistor in the splitter.
            R2 (float): Resistance value in Ohms of the first output resistor.
            R3 (float): Resistance value in Ohms of the second output resistor.

        """
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
        """
        Calculate and return the Thenevin voltage for the two output branches
        
        Args:
            time_array (np.ndarray): Array of signal's time values in seconds.
            open_volts_array (np.ndarray): Corresponding open circuit voltage values to be fed into branch 1 at each time bin in time_array.
            load_1_impedance (float): Impedance of the load connected to the first branch.
            load_2_impedance (float): Impedance of the load connected to the second branch.
            source_impedance (float): Impedance of the device connected to the first branch 
            signal_baseline (float): Signal baseline. May be 0.0 or a DC offset 

        Return:
            time_array (np.ndarray): original time array.
            open_circuit_output_1 (np.ndarray): open-cirtuit voltage array without the on branch 1 load applied.
            output_impedance_1 (float): equivalent impedance of the splitter circuit when load 1 is disconnected.
            open_circuit_output_2 (np.ndarray): open-cirtuit voltage array without the on branch 2 load applied.
            output_impedance_2 (float): equivalent impedance of the splitter circuit when load 2 is disconnected.

        """
        
        if len(time_array) != len(open_volts_array):
            raise ValueError("Time and Voltage array must be equal in length")

        pulse_voltage = open_volts_array  - signal_baseline
        #assume cable offers no imp.
        
        #source impedance and the first resistor are in series. Added to get total impedenece of the input branch
        source_side_impedance =  source_impedance + self.R1

        #The impedance of the load and the resistors corresponding to their branch are also in series. 
        #Added to get total impedance of branches 1 and 2 
        branch_1_impedance = self.R2 + load_1_impedance
        branch_2_impedance = self.R3 + load_2_impedance
        
        
        open_circuit_output_1 = ( signal_baseline + self.voltage_divider( pulse_voltage, source_side_impedance, branch_2_impedance ) )
        #From the perspective of the load on branch one, the input branch and branch two are in parallel 
        output_impedance_1 = (self.R2 + self.get_parallel_impedance( source_side_impedance, branch_2_impedance) )

        open_circuit_output_2 = ( signal_baseline + self.voltage_divider( pulse_voltage, source_side_impedance, branch_1_impedance) )
        output_impedance_2 = ( self.R3 + self.get_parallel_impedance( source_side_impedance, branch_1_impedance ) )

        return ( time_array, open_circuit_output_1, output_impedance_1, open_circuit_output_2, output_impedance_2 )
