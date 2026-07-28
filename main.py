import random

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spline_filter
from ComponentClasses import (  Amplifier, Connector, 
                                Digitizer, 
                                Cable,
                                Generator,
                                Terminator, 
                                Splitter, 
                                EdgeDiscriminator,
                                CircuitAnalyzer)


generator = Generator()
splitter = Splitter(16.5, 16.5, 16.5)
digitizer = Digitizer()
analyzer = CircuitAnalyzer()

num_seconds = 100e-9
num_samples = 5000

time_array = np.linspace(0,num_seconds, num_samples)
# voltage_array = generator.get_PMT_signal(expected_photoelectrons = 40, time_array = time_array, t_0 = 10e-9, Tau_fall=2.1e-9, Tau_rise=0.9e-9, Tau_fall_spe = 6e-9 , Tau_rise_spe = 2e-9, polarity=1)


# event_times = np.array([np.random.uniform(0, time_array[-1]),np.random.uniform(0, time_array[-1]), np.random.uniform(0, time_array[-1]) ])
event_times = np.array([np.random.uniform(0, time_array[-1000]),np.random.uniform(0, time_array[-1000]), np.random.uniform(0, time_array[-1000]) ])

Tau_fall = np.array([2.1e-9, 2.1e-9, 2.1e-9])
Tau_rise = np.array([0.9e-9, 0.9e-9, 0.9e-9])
Tau_fall_spe  = np.array([6e-9, 6e-9, 6e-9])
Tau_rise_spe  = np.array([2e-9, 2e-9, 2e-9])

voltage_array = generator.get_PMT_event_train(  time_array = time_array,
                                                event_times = event_times,
                                                expected_photoelectrons = 40,
                                                polarity = 1,
                                                Tau_fall = Tau_fall,
                                                Tau_rise = Tau_rise,
                                                Tau_fall_spe = Tau_fall_spe,  
                                                Tau_rise_spe = Tau_rise_spe,
                                                )
                                                

split_results = splitter.split(time_array, voltage_array, load_1_impedance = 50,load_2_impedance = 50, source_impedance = generator.output_impedance)
signal_a = split_results[1]
signal_b = split_results[3]

_, loaded_voltage = Connector.connect(time_array, signal_b, split_results[4], digitizer.input_impedance,)

(
    digitized_time,
    ADC_codes,
    reconstructed_voltage,
    was_clipped
) = digitizer.digitize(
    time_array = time_array,
    loaded_voltage_array = loaded_voltage,
    sampling_rate_Hz = 2e9,
    num_bits = 12,
    min_volts = -1.0,
    max_volts = 1.0
)

analyzer.record_stage(
    name="PMT output",
    time_array=time_array,
    voltage_array=voltage_array,
    polarity=1,
    component_name="Generator",
    voltage_type="open_circuit",
    baseline=0.0,
    source_impedance=generator.output_impedance,
)

analyzer.record_stage(
    name="Splitter channel 2",
    time_array=time_array,
    voltage_array=signal_b,
    polarity=1,
    component_name="Splitter",
    voltage_type="open_circuit",
    baseline=0.0,
    source_impedance=split_results[4],
    load_impedance=digitizer.input_impedance,
)

analyzer.record_stage(
    name="Digitizer input",
    time_array=time_array,
    voltage_array=loaded_voltage,
    polarity=1,
    component_name="Digitizer",
    voltage_type="loaded",
    baseline=0.0,
    source_impedance=split_results[4],
    load_impedance=digitizer.input_impedance,
    adc_codes=ADC_codes,
    was_clipped=was_clipped,
)

for stage_name in analyzer.stages:
    analyzer.display_diagnostics(stage_name)


plt.plot(time_array, voltage_array, color="green", label="Original Signal")
plt.plot(time_array, signal_b, color="blue", label="Split Channel 2 : not loaded")
plt.step(digitized_time, reconstructed_voltage, color="black", label="Digitized Split Channel 2")

plt.xlabel("Time (s)")
plt.ylabel("Amplitude of Photomultiplier tube Signal (V)")

plt.legend()
plt.grid(True)

plt.show()
