import numpy as np
import matplotlib.pyplot as plt
# plt.style.use('dark_background')
from ComponentClasses import (  Amplifier, Connector, 
                                Digitizer, 
                                Cable,
                                Generator,
                                Terminator, 
                                Splitter, 
                                EdgeDiscriminator,
                                CircuitAnalyzer)



velocity_factor = .66
attenuation_db_per_m = .30
cable_characteristic_impedance = 50

num_seconds = 150e-9
num_samples = 10_000

time_array = np.linspace(0, num_seconds, num_samples)


amplifier = Amplifier(  gain = 2, 
                        gain_units = "unitless", 
                        input_impedance = 50, 
                        output_impedance = 50, 
                        min_voltage_out = -2.0,
                        max_voltage_out = 2.0, 
                        slew_rate_down = -np.inf, 
                        slew_rate_up = np.inf,
                        high_cutoff_freq = 250e6 
                        )

digitizer = Digitizer(input_impedance = 50)

rng = np.random.default_rng(seed = 60)

"""====================== GENERATOR INITIALIZATION ======================"""
generator_output_impedance = 50
generator = Generator(output_impedance = generator_output_impedance)

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
                                            random_seed = 1
                                            ) 

generated_signal  = generator.get_PMT_event_train(
                                            expected_photoelectrons = expected_photoelectrons,
                                            time_array = time_array,
                                            event_times = rng.uniform(low=0.0, high = num_seconds * (3/4), size=3),
                                            Tau_fall = np.array([Tau_fall, Tau_fall, Tau_fall]),
                                            Tau_rise = np.array([Tau_rise, Tau_rise, Tau_rise]),
                                            Tau_rise_spe = np.array([Tau_rise_spe, Tau_rise_spe, Tau_rise_spe]),
                                            Tau_fall_spe = np.array([Tau_fall_spe, Tau_fall_spe, Tau_fall_spe]),
                                            polarity = polarity,
                                            random_seeds = np.array([1,2,3])
                                            ) 

"""====================== CABLE 1 INITIALIZATION ======================"""

cable_length_meters = 1 
cable_to_amplifier = Cable( length_m = cable_length_meters,
                            velocity_factor = velocity_factor,
                            attenuation_db_per_m = attenuation_db_per_m,
                            characteristic_impedance = cable_characteristic_impedance
                            )

_, amplifier_input_signal = cable_to_amplifier.propagation( time_array = time_array, 
                                                open_circuit_voltage_array =  generated_signal,
                                                source_impedance = generator.output_impedance,
                                                load_impedance = amplifier.input_impedance, 
                                                signal_baseline = 0.0,
                                                max_round_trips = 5

                                                )


"""====================== AMPLIFIER INITIALIZATION ======================"""

_, amplified_signal = amplifier.amplify(time_array = time_array,
                                        loaded_voltage_array = amplifier_input_signal,
                                        signal_baseline = 0.0,
                                        )


"""====================== CABLE 2 INITALIZATION ======================"""

cable_2_length_meters = 5


cable_to_digitizer = Cable( length_m = cable_2_length_meters,
                            velocity_factor = velocity_factor,
                            attenuation_db_per_m = attenuation_db_per_m,
                            characteristic_impedance = 100
                            )

_, digitizer_input_signal = cable_to_digitizer.propagation( time_array = time_array, 
                                                open_circuit_voltage_array =  amplified_signal,
                                                source_impedance = amplifier.output_impedance,
                                                load_impedance = digitizer.input_impedance, 
                                                signal_baseline = 0.0,
                                                max_round_trips = 100
                                                )

"""====================== DIGITIZER INITIALIZATION ======================"""

discrete_times, Digitized_array, Reconstructed_array, was_clipped = digitizer.digitize(time_array = time_array,
                                                                                        loaded_voltage_array = digitizer_input_signal,
                                                                                        sampling_rate_Hz = 3.2e9, 
                                                                                        num_bits = 12,
                                                                                        min_volts = -1.25,
                                                                                        max_volts = 1.25,
                                                                                        dc_offset = 0.0) 

plt.plot(
    time_array * 1e9,
    generated_signal * 1e3,
    color = "blue",
    label = "PMT open-circuit output"
)

plt.plot(
    time_array * 1e9,
    amplifier_input_signal * 1e3,
    color = "purple",
    label = "Amplifier input after 1 m cable"
)

plt.plot(
    time_array * 1e9,
    amplified_signal * 1e3,
    color = "green",
    label = "Amplifier open-circuit output"
)

plt.plot(
    time_array * 1e9,
    digitizer_input_signal * 1e3,
    color = "navy",
    label = "Digitizer analog input"
)

plt.step(
    discrete_times * 1e9,
    Reconstructed_array * 1e3,
    color = "red",
    label = "Digitizer samples"
)

plt.xlabel("Time (ns)", fontsize = 20)
plt.ylabel("Voltage (mV)", fontsize = 20)
plt.title("PMT Analog Signal Chain", fontsize = 20)

plt.legend()
# plt.grid(True)

plt.show()