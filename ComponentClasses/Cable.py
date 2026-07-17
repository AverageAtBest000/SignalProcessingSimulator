import numpy as np
import scipy.constants as constants

class Cable:
    
    def __init__(self, characteristic_impedance, length_m, velocity_factor, attenuation_db_per_m):

        self.validate_constructor_params(characteristic_impedance, length_m, velocity_factor, attenuation_db_per_m)
        self.characteristic_impedance = characteristic_impedance
        self.length_m = length_m
        self.velocity_factor = velocity_factor
        self.attenuation_db_per_m = attenuation_db_per_m

    def validate_constructor_params(self, characteristic_impedance, length_m, velocity_factor, attenuation_db_per_m):
        if not np.isfinite(characteristic_impedance) or characteristic_impedance <= 0:
            raise ValueError("characteristic_impedance must be finite and greater than zero")
        if not np.isfinite(length_m) or length_m < 0:
            raise ValueError("length_m must be finite and not negative")
        if not np.isfinite(velocity_factor) or not 0 < velocity_factor <= 1:
            raise ValueError("velocity_factor must be greater than zero and 1 >= ")
        if not np.isfinite(attenuation_db_per_m) or attenuation_db_per_m < 0:
            raise ValueError("attenuation_db_per_m must be finite and not negative")


    def propagation(self, time_array, voltage_array, source_impedance, load_impedance, signal_baseline, max_round_trips, volts_in_is_open_circuit = True):
        
        pulse_voltage = voltage_array - signal_baseline
        delay = self.calculate_delay()

        attenuation = self.get_attenuation()

        load_reflection = self.get_reflection_coefficient(load_impedance)

        source_reflection = self.get_reflection_coefficient(source_impedance)

        if volts_in_is_open_circuit:
            launch_factor = self.characteristic_impedance / (source_impedance + self.characteristic_impedance)
        else:
            launch_factor = 1.0

        launched_wave  = pulse_voltage * launch_factor

        current_incident_wave = launched_wave * attenuation

        current_arrival_delay = delay

        output_voltage_change = np.zeros(len(voltage_array))
        
        for round_trip in range(max_round_trips):
            
            if current_arrival_delay > time_array[-1]:
                break
            
            delayed_incident_wave = self.delay_wave(
                                                    time_array,
                                                    voltage_array = current_incident_wave,  
                                                    delay = current_arrival_delay
                                                    )
            
            load_contribution = delayed_incident_wave * (1 + load_reflection)

            output_voltage_change = output_voltage_change + load_contribution

            current_incident_wave =  current_incident_wave * load_reflection * source_reflection * (attenuation ** 2)

            current_arrival_delay = current_arrival_delay + (2 * delay)

        output_voltage = signal_baseline + output_voltage_change

        return time_array, output_voltage
        pass

    def validate_method_params(self, time_array, voltage_array, source_impedance, load_impedance, signal_baseline, max_round_trips):

        if time_array.ndim != 1 or voltage_array.ndim != 1:
            raise ValueError("time_array and voltage_array must be in 1D")
        if len(time_array) != len(voltage_array) or len(time_array) < 2:
            raise ValueError("time_array and voltage_array must be equal in length and contain at least two samples")
        if not np.all(np.isfinite(time_array)) or not np.all(np.isfinite(voltage_array)):
            raise ValueError("time_array and voltage_array must not contain infinite values")
        if np.any(np.diff(time_array) <= 0):
            raise ValueError("time_array must be increasing")
        if not np.isfinite(signal_baseline):
            raise ValueError("signal_baseline must be finite")

    def calculate_delay(self):

        propagation_speed = self.velocity_factor * constants.speed_of_light
        delay = self.length_m / propagation_speed

        return delay

    def get_reflection_coefficient(self, impedance):

        if np.isinf(impedance):
            return 1.0

        reflection_coefficient  = (impedance - self.characteristic_impedance) / (impedance + self.characteristic_impedance)

        return reflection_coefficient

    def get_attenuation(self):
        
        loss = self.attenuation_db_per_m * self.length_m
        atten_factor = 10 ** (- loss / 20)
        
        return atten_factor


    def delay_wave(self, time_array, voltage_array, delay):

        new_time_array = time_array - delay
        delayed_wave = np.interp( x = new_time_array, xp = time_array, fp = voltage_array, left = 0, right = 0)

        return delayed_wave
    