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
                                EdgeDiscriminator)



generator = Generator()
splitter = Splitter(16.5, 16.5, 16.5)
digitizer = Digitizer()

num_seconds = 100e-9
num_samples = 5000

time_array = np.linspace(0,num_seconds, num_samples)
# voltage_array = generator.get_PMT_signal(expected_photoelectrons = 40, time_array = time_array, t_0 = 10e-9, Tao_fall=2.1e-9, Tao_rise=0.9e-9, Tao_fall_spe = 6e-9 , Tao_rise_spe = 2e-9, polarity=1)


# event_times = np.array([np.random.uniform(0, time_array[-1]),np.random.uniform(0, time_array[-1]), np.random.uniform(0, time_array[-1]) ])
event_times = np.array([np.random.uniform(0, time_array[-1000]),np.random.uniform(0, time_array[-1000]), np.random.uniform(0, time_array[-1000]) ])

Tao_fall = np.array([2.1e-9, 2.1e-9, 2.1e-9])
Tao_rise = np.array([0.9e-9, 0.9e-9, 0.9e-9])
Tao_fall_spe  = np.array([6e-9, 6e-9, 6e-9])
Tao_rise_spe  = np.array([2e-9, 2e-9, 2e-9])

voltage_array = generator.get_PMT_event_train(  time_array = time_array,
                                                event_times = event_times,
                                                expected_photoelectrons = 40,
                                                polarity = 1,
                                                Tao_fall = Tao_fall,
                                                Tao_rise = Tao_rise,
                                                Tao_fall_spe = Tao_fall_spe,  
                                                Tao_rise_spe = Tao_rise_spe,
                                                )
                                                

split_results = splitter.split(time_array, voltage_array, load_1_impedance = 50,load_2_impedance = 50, source_impedance = 50)
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




plt.plot(time_array, voltage_array, color="green", label="Original Signal")
plt.plot(time_array, signal_b, color="blue", label="Split Channel 2 : not loaded")
plt.step(digitized_time, reconstructed_voltage, color="black", label="Digitized Split Channel 2")

plt.xlabel("Time (s)")
plt.ylabel("Amplitude of Photomultiplier tube Signal (V)")

plt.legend()
plt.grid(True)

plt.show()
