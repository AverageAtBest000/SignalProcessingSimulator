import numpy as np
import matplotlib.pyplot as plt
from SignalGenerator import Generator
from Splitter import Splitter

generator = Generator()
splitter = Splitter(16.5, 16.5, 16.5)

num_seconds = 100e-9
num_samples = 5000

time_array = np.linspace(0,num_seconds, num_samples)
voltage_array = generator.get_PMT_signal(expected_photoelectrons = 40, time_array = time_array, t_0 = 10e-9, Tao_fall=2.1e-9, Tao_rise=0.9e-9, Tao_fall_spe = 6e-9 , Tao_rise_spe = 2e-9, polarity=1)

split_results = splitter.split(time_array, voltage_array, load_1_impedance = 50,load_2_impedance = 5, source_impedance = 50)
signal_a = split_results[1]
signal_b = split_results[2]

plt.plot(time_array, voltage_array, color="green", label="Original Signal")
plt.plot(time_array, signal_a, color="red", label="Split Channel 1")
plt.plot(time_array, signal_b, color="black", label="Split Channel 2")

plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.legend()
plt.grid(True)

plt.show()
