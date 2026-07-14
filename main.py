import numpy as np
import matplotlib.pyplot as plt
import scipy
from signalGeneration import Generator


generator = Generator()

num_seconds = 100e-9
num_samples = 5000

X = np.linspace(0,num_seconds, num_samples)
Y = generator.get_PMT_signal(A = 100, T = X, t_0 = 10, Tao_fall_nano=2.1, Tao_rise_nano=0.9, Tao_fall_spe_nano = 6 , Tao_rise_spe_nano = 2)

plt.plot(X,Y)
plt.show() 
