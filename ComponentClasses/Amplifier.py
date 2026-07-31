import numpy as np
import scipy.signal as signal

class Amplifier:
    #saturating upper/lower can extend signals

    def __init__(self, 
                 gain, 
                 gain_units, 
                 input_impedance, 
                 output_impedance, 
                 min_voltage_out, 
                 max_voltage_out, 
                 slew_rate_up = np.inf, 
                 slew_rate_down = -np.inf, 
                 input_noise_rms=0.0,
                 output_noise_rms=0.0,
                 low_cutoff_freq = None, 
                 high_cutoff_freq = None,
                 random_seed = None
                ):
                

        """
        Store the amplifiers physical properties 

        Args:
            gain (float): value that scales the signal 
            gain_units (str): Units of the previously provided gain. May be "unitless" or "dB".
            input_impedance (float): impedance of the amplifier's input port. 
            output_impedance (float): impedance of the amplifier's output port. 
            min_voltage_out (float): minimum voltage outputed by the amplifier
            max_voltage_out (float): maximum voltage outputed by the amplifier
            slew_rate_up (float): slew rate when signal has a positive gradient
            slew_rate_down (float): slew rate when signal has a negative gradient
            input_noise_rms (float): RMS noise voltage added before gain.
            output_noise_rms (float): RMS noise voltage added after gain.
            low_cutoff_freq (float): cutoff for the high pass filter
            high_cutoff_freq (floar): cutoff for the low pass filter
        """




        self.validate_constructor_params(gain, gain_units, min_voltage_out, max_voltage_out, low_cutoff_freq, high_cutoff_freq, output_impedance, input_impedance, slew_rate_up, slew_rate_down)

        self.low_cutoff_freq = low_cutoff_freq
        self.high_cutoff_freq = high_cutoff_freq
        self.input_impedance = input_impedance
        self.output_impedance = output_impedance
        self.max_voltage_out = max_voltage_out
        self.min_voltage_out = min_voltage_out
        self.slew_rate_up = slew_rate_up
        self.slew_rate_down = slew_rate_down
        self.input_noise_rms = input_noise_rms
        self.output_noise_rms = output_noise_rms
        self.random_seed = random_seed

    def amplify(self, time_array: np.ndarray, loaded_voltage_array: np.ndarray, signal_baseline: float, output_baseline: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
        
        """

        Apply the load of a component the to the open circut voltage of the preceding component 

        Args:
            time_array (np.ndarray): Array of signal's time values in seconds.
            loaded_voltage_array (np.ndarray): Corresponding loaded voltage values at each time bin in time_array. 
            signal_baseline (float): Signal baseline. May be 0.0 or a DC offset
            output_baseline (float): Signal baseline applied by the amplifier and not included in the original signal. 
        Return:
            time_array (np.ndarray): original time array.
            open_circuit_aplified_voltage (np.ndarray): Array of voltage values after amplification without the load applied 
        
        """
        rng = np.random.default_rng(self.random_seed)

        self.validate_params(time_array, loaded_voltage_array)

        time_delta = time_array[1] - time_array[0]

        sampling_frequency = 1 / time_delta
        
        nyquist_frequency = sampling_frequency / 2

        amplified_voltage = loaded_voltage_array - signal_baseline
        
        amplified_voltage = amplified_voltage * self.gain

        input_noise = rng.normal( loc=0.0, scale=self.input_noise_rms, size=len(amplified_voltage) )


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

        open_circuit_amplified_voltage = self.apply_soft_saturation( voltage_array = open_circuit_amplified_voltage, output_baseline = output_baseline, min_voltage_out = self.min_voltage_out, max_voltage_out = self.max_voltage_out)
        
        open_circuit_amplified_voltage = self.apply_slew_rates(open_circuit_amplified_voltage, self.slew_rate_up, self.slew_rate_down, time_delta)

        return time_array, open_circuit_amplified_voltage


    @classmethod
    def apply_slew_rates(cls, open_circuit_amplified_voltage, slew_rate_up, slew_rate_down, time_delta):
        max_voltage_delta_up = slew_rate_up * time_delta
        max_voltage_delta_down = slew_rate_down * time_delta

        for i in range(1, len(open_circuit_amplified_voltage)):

            current_delta = open_circuit_amplified_voltage[i] - open_circuit_amplified_voltage[i-1]

            if current_delta > max_voltage_delta_up:
                open_circuit_amplified_voltage[i] = open_circuit_amplified_voltage[i-1] + max_voltage_delta_up 

            elif current_delta < max_voltage_delta_down:
                open_circuit_amplified_voltage[i] = open_circuit_amplified_voltage[i-1] + max_voltage_delta_down 
                
        return open_circuit_amplified_voltage


    def validate_params(self, time_array, loaded_voltage_array):
        
        if len(time_array) != len(loaded_voltage_array) or len(time_array) < 2:
            raise ValueError("loaded_voltage_array and time_array must be of equal length and have at least two samples")
        
        if self.high_cutoff_freq is not None:
            if self.high_cutoff_freq <= 0:
                raise ValueError("high_cutoff_freq and low_cutoff_freq must be greater than 0")
        
        if self.low_cutoff_freq is not None:
            if self.low_cutoff_freq <= 0:
                raise ValueError("high_cutoff_freq and low_cutoff_freq must be greater than 0")

    
    def validate_constructor_params(self, gain, gain_units, min_voltage_out, max_voltage_out, low_cutoff_freq, high_cutoff_freq, output_impedance, input_impedance, slew_rate_up, slew_rate_down):

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
        
        if slew_rate_down >= 0:
            raise ValueError("slew_rate_down must be less than zero")

        if slew_rate_up <= 0:
            raise ValueError("slew_rate_up must be greater than zero")


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


    @classmethod
    def apply_soft_saturation( cls, voltage_array, output_baseline, min_voltage_out, max_voltage_out ):

        soft_saturated_voltage = np.zeros(len(voltage_array))

        positive_values = voltage_array >= output_baseline
        negative_values = voltage_array < output_baseline

        positive_headroom = max_voltage_out - output_baseline
        negative_headroom = output_baseline - min_voltage_out

        soft_saturated_voltage[positive_values] = ( output_baseline + positive_headroom * np.tanh( ( voltage_array[positive_values] - output_baseline ) / positive_headroom ) )

        soft_saturated_voltage[negative_values] = ( output_baseline + negative_headroom * np.tanh( ( voltage_array[negative_values] - output_baseline ) / negative_headroom ) )

        return soft_saturated_voltage