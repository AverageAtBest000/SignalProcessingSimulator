import numpy as np
import scipy.constants as constants

class Cable:
    
    def __init__(self, characteristic_impedance, length_m, velocity_factor, attenuation_db_per_m):

        self.characteristic_impedance = characteristic_impedance
        self.length_m = length_m
        self.velocity_factor = velocity_factor
        self.attenuation_db_per_m = attenuation_db_per_m

    
    def propagation(self, time_array, voltage_array, source_impedance, load_impedance, signal_baseline, max_round_trips):
        
        pulse_voltage = voltage_array - signal_baseline
        delay = self.calculate_delay()

        attenuation = self.get_atteniation()

        load_reflection = self.get_reflection_coefficient(load_impedance)

        source_reflection = self.get_reflection_coefficient(source_impedance)

        launch_factor = self.characteristic_impedance / (source_impedance + self.characteristic_impedance)

        launched_wave  = pulse_voltage * launch_factor

        current_incident_wave = launched_wave * attenuation

        current_arrival_delay = delay

        output_voltage_change = np.zeros(len(voltage_array))
        
        for round_trip in max_round_trips:
            
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

    def calculate_delay(self):

        propagation_speed = self.velocity_factor * constants.speed_of_light
        delay = self.length_m / propagation_speed

        return delay

    def get_reflection_coefficient(self, impedance):

        reflection_coefficient  = (impedance - self.characterist) / (impedance + self.characterist)

        return reflection_coefficient

    def get_atteniation(self):
        
        loss = self.attenuation_db_per_m * self.length_m
        atten_factor = 10 ** (- loss / 20)
        
        return atten_factor


    def delay_wave(self, time_array, voltage_array, delay):

        new_time_array = time_array - delay
        delayed_wave = np.interp( x = new_time_array, xp = time_array, fp = voltage_array)

        return delayed_wave
    