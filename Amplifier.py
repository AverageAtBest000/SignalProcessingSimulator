import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats


class Amplifier:
    
    def __init__():
        pass

    def amplify(time_array, voltage_array, gain, signal_baseline, low_cutoff_freq, high_cutoff_freq, source_impedence, gain_units = "unitless"):
        
        if len(time_array) != len(voltage_array):
            raise ValueError("voltage_array and time_array must be of equal length")

        time_delta = t[1] - t[0]

        sampling_frequency = 1 / time_delta
        nyquist_frequency = sampling_frequency / 2

        amplified_voltage = voltage_array - signal_baseline
        
        if gain_units.lower() == "db":
                gain = 10 ** (gain/20)

        amplified_voltage = amplified_voltage * gain

        return time_array, amplified_voltage
