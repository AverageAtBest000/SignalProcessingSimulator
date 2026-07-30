import numpy as np
import matplotlib.pyplot as plt
plt.style.use('dark_background')
from ComponentClasses import (  Amplifier, Connector, 
                                Digitizer, 
                                Cable,
                                Generator,
                                Terminator, 
                                Splitter, 
                                EdgeDiscriminator,
                                CircuitAnalyzer)




num_seconds = 100e-9
num_samples = 10_000

time_array = np.linspace(0, num_seconds, num_samples)


amplifier = Amplifier( 500, "unitless", 50, 50, -np.inf, np.inf, slew_rate_down = -np.inf, slew_rate_up = np.inf)
digitizer = Digitizer(input_impedance = 60)

"""====================== GENERATOR INITIALIZATION ======================"""
generator_output_impedance = 50
generator = Generator(output_impedance = 50)

expected_photoelectrons = 20
signal_start_time = 20e-9
Tau_fall = 2.1e-9
Tau_rise = 0.9e-9
Tau_fall_spe = 6e-9 
Tau_rise_spe = 2e-9
polarity = -1
generated_signal  = generator.get_PMT_signal(
                                            expected_photoelectrons = expected_photoelectrons,
                                            time_array = time_array,
                                            t_0 = signal_start_time,
                                            Tau_fall = Tau_fall ,
                                            Tau_rise = Tau_rise,
                                            Tau_rise_spe = Tau_rise_spe,
                                            Tau_fall_spe = Tau_fall_spe,
                                            polarity = polarity,
                                            ) 


"""====================== CABLE 1 INITIALIZATION ======================"""

cable_length_meters = 1 
velocity_factor = .7
attenuation_db_per_m = 50

cable_to_amplifier = Cable( length_m = cable_length_meters,
                            velocity_factor = velocity_factor,
                            attenuation_db_per_m = attenuation_db_per_m,
                            characteristic_impedance = 50
                            )

_, voltage_array = cable_to_amplifier.propagation( time_array = time_array, 
                                                open_circuit_voltage_array =  generated_signal,
                                                source_impedance = generator.output_impedance,
                                                load_impedance = amplifier.input_impedance, 
                                                signal_baseline = 0.0,
                                                max_round_trips = 100

                                                )


"""====================== AMPLIFIER INITIALIZATION ======================"""

_, amplified_signal = amplifier.amplify(time_array = time_array,
                                        loaded_voltage_array = voltage_array,
                                        signal_baseline = 0.0,
                                        )


"""====================== CABLE 2 INITALIZATION ======================"""

cable_2_length_meters = 5
velocity_factor = .7
attenuation_db_per_m = 50

cable_to_digitizer = Cable( length_m = cable_2_length_meters,
                            velocity_factor = velocity_factor,
                            attenuation_db_per_m = attenuation_db_per_m,
                            characteristic_impedance = 50
                            )

_, voltage_array = cable_to_digitizer.propagation( time_array = time_array, 
                                                open_circuit_voltage_array =  generated_signal,
                                                source_impedance = amplifier.output_impedance,
                                                load_impedance = digitizer.input_impedance, 
                                                signal_baseline = 0.0,
                                                max_round_trips = 100
                                                )

"""====================== DIGITIZER INITIALIZATION ======================"""

discrete_times, Digitized_array, Reconstructed_array, was_clipped = digitizer.digitize(time_array = time_array,
                                      loaded_voltage_array = voltage_array,
                                      sampling_rate_Hz = 2e9, 
                                      num_bits = 12,
                                      min_volts = -1.0,
                                      max_volts = 1.0) 

plt.plot(time_array, generated_signal, color="blue", label="Original Signal")
plt.plot(time_array, amplified_signal, color="white", label="Amplified Signal")
plt.plot(discrete_times, Reconstructed_array, color="red", label="Digitized Signal")

plt.xlabel("Time (s)")
plt.ylabel("Amplitude of Photomultiplier tube Signal (V)")

plt.legend()
plt.grid(True)

plt.show()

