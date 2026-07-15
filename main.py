import numpy as np
import matplotlib.pyplot as plt
import scipy
from SignalGenerator import Generator


generator = Generator()

num_seconds = 100e-9
num_samples = 5000

X = np.linspace(0,num_seconds, num_samples)
Y = generator.get_PMT_signal(expected_photoelectrons = 50, time_array = X, t_0 = 10e-9, Tao_fall=2.1e-9, Tao_rise=0.9e-9, Tao_fall_spe = 6e-9 , Tao_rise_spe = 2e-9, polarity=1)

plt.plot(X,Y)
plt.show() 
