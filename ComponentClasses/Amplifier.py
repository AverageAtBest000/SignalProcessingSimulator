import numpy as np
import scipy.signal as signal

class Amplifier:
    #saturating upper/lower can extend signals
    def __init__(self, gain, gain_units, input_impedance, output_impedance, min_voltage_out, max_voltage_out, low_cutoff_freq = None, high_cutoff_freq = None):
    # just use unitless
        if gain_units.lower() == "db":
            self.gain = 10 ** (gain/20)
        elif gain_units.lower() == "unitless":
            self.gain = gain        
        else: 
            raise ValueError("Invalid gain unit. Use \"db\" or \"unitless\" ")

        if min_voltage_out > max_voltage_out:
            raise ValueError("max_voltage_out must be greater than min_voltage_out")

        if low_cutoff_freq is not None and high_cutoff_freq is not None:
            if low_cutoff_freq > high_cutoff_freq:
                raise ValueError("high_cutoff_freq must be greater than low_cutoff_freq")

        if input_impedance < 0 or output_impedance < 0:
            raise ValueError("input_impedance and output_inpedance must be greater than zero")

        self.low_cutoff_freq = low_cutoff_freq
        self.high_cutoff_freq = high_cutoff_freq
        self.input_impedance = input_impedance
        self.output_impedance = output_impedance
        self.max_voltage_out = max_voltage_out
        self.min_voltage_out = min_voltage_out


    def amplify(self, time_array: np.ndarray, loaded_voltage_array: np.ndarray, signal_baseline: float, output_baseline: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    # some of this only aplies to RF signal
        

        time_delta = time_array[1] - time_array[0]

        sampling_frequency = 1 / time_delta
        
        nyquist_frequency = sampling_frequency / 2

        amplified_voltage = loaded_voltage_array - signal_baseline
        
        amplified_voltage = amplified_voltage * self.gain

        if self.low_cutoff_freq is not None:
            if self.low_cutoff_freq < nyquist_frequency:    
                amplified_voltage = self.apply_low_freq_cutoff(amplified_voltage, self.low_cutoff_freq, time_delta)
            else:
                raise ValueError("low_cutoff_freq must be less than the nyquist")

        if self.high_cutoff_freq is not None:
            if self.high_cutoff_freq < nyquist_frequency:
                amplified_voltage = self.apply_high_freq_cutoff(amplified_voltage, self.high_cutoff_freq, time_delta)
            else:
                raise ValueError("high_cutoff_freq must be less than the nyquist")

        open_circuit_amplified_voltage = amplified_voltage + output_baseline

        open_circuit_amplified_voltage = np.clip(open_circuit_amplified_voltage, self.min_voltage_out, self.max_voltage_out)

        return time_array, open_circuit_amplified_voltage

    def validate_params(self, time_aray, voltage_array):
        
        if len(time_array) != len(loaded_voltage_array) or len(time_array) < 2:
            raise ValueError("loaded_voltage_array and time_array must be of equal length and have at least two samples")
        
        if self.high_cutoff_freq < 0 or self.low_cutoff_freq < 0:
            raise ValueError("high_cutoff_freq and low_cutoff_freq must be greater than 0")

    @classmethod
    def apply_high_freq_cutoff(cls, voltage_in, cutoff_frequency, time_delta):
        
        alpha = cls.get_alpha(time_delta = time_delta, frequency=cutoff_frequency)

        voltage_in_coefficient = [alpha]
        output_coefficients = [1.0 , -(1.0 - alpha)]

        initial_value = voltage_in[0]
        initial_filter_state = np.array([initial_value * (1.0 - alpha)])

        filtered_voltage, _ = signal.lfilter(
            b=voltage_in_coefficient, 
            a=output_coefficients, 
            x=voltage_in, 
            zi=initial_filter_state
        )
        
        return filtered_voltage


    @classmethod
    def apply_low_freq_cutoff(cls, voltage_in, cutoff_frequency, time_delta):
        
        alpha = cls.get_alpha(time_delta = time_delta, frequency=cutoff_frequency)

        voltage_in_coefficient = [alpha]
        output_coefficients = [1.0 , -(1.0 - alpha)]

        initial_value = voltage_in[0]
        initial_filter_state = np.array([initial_value * (1.0 - alpha)])

        filtered_voltage, _ = signal.lfilter(
            b=voltage_in_coefficient, 
            a=output_coefficients, 
            x=voltage_in, 
            zi=initial_filter_state
        )
        
        return voltage_in - filtered_voltage
            
    @classmethod
    def get_alpha(cls, time_delta, frequency):
        
        tao_L = 1 / (2 * np.pi * frequency)
        alpha = 1 - np.exp( (-time_delta) / tao_L )
        return alpha