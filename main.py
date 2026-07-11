import numpy as np
import matplotlib.pyplot as plt
import scipy
from signalGeneration import Generator


num_miscroseconds = 10
num_samples= 500

X = np.linspace(0,num_miscroseconds, num_samples)
Y = Generator.get_PMT_signal(10, X, 0, 1.9, 0.3)

plt.plot(X,Y)
plt.show() 
