from typing import Self
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal


class Amplifier:
    
    def __init__(self, gain, gain_units, source_impedence, output_impedence, low_cutoff_freq = None, high_cutoff_freq = None):
        
        if gain_units.lower() == "db":
            self.gain = 10 ** (gain/20)
        elif gain_units.lower() == "unitless":
            self.gain = gain        
        else: 
            raise ValueError("Invalid gain unit. Use \"db\" or \"unitless\" ")

        self.low_cutoff_freq = low_cutoff_freq
        self.high_cutoff_freq = high_cutoff_freq
        self.source_impedence = source_impedence
        self.output_impedence = output_impedence


    def amplify(self, time_array, voltage_array, signal_baseline):
        
        if len(time_array) != len(voltage_array) or len(time_array) < 2:
            raise ValueError("voltage_array and time_array must be of equal length and have at least two samples")

        time_delta = time_array[1] - time_array[0]

        sampling_frequency = 1 / time_delta
        nyquist_frequency = sampling_frequency / 2

        amplified_voltage = voltage_array - signal_baseline
        
        amplified_voltage = amplified_voltage * self.gain

        if self.low_cutoff_freq is not None:
            amplified_voltage = self.apply_freq_cutoff(amplified_voltage, self.low_cutoff_freq, time_delta)

        if self.high_cutoff_freq is not None:
            amplified_voltage = self.apply_freq_cutoff(amplified_voltage, self.high_cutoff_freq, time_delta)

        return time_array, amplified_voltage


    @classmethod
    def apply_freq_cutoff(cls, voltage_in, cutoff_frequency, time_delta):
        
        alpha = cls.get_alpha(time_delta = time_delta, frequency=cutoff_frequency)

        voltage_in_coefficient = [alpha]
        output_coefficients = [1.0 , -(1.0 - alpha)]

        initial_value = voltage_in[0]
        initial_filter_state = np.array([initial_value * (1.0 - alpha)])

        voltage_slow, _ = signal.lfilter(
            b=voltage_in_coefficient, 
            a=output_coefficients, 
            x=voltage_in, 
            zi=initial_filter_state
        )
        
        return voltage_slow
            
    @classmethod
    def get_alpha(cls, time_delta, frequency):
        
        tao_L = 1 / (2 * np.pi * frequency)
        alpha = 1 - np.exp( (-time_delta) / tao_L )
        return alpha