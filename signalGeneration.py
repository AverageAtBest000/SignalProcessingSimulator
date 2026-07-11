import numpy as np
import matplotlib.pyplot as plt
import scipy

class Generator: 
    
    @staticmethod
    def get_PMT_signal(A, T, t_0, Tao_fall, Tao_rise):
        return   A * ( np.exp(-(T-t_0)/Tao_fall) - np.exp( -(T-t_0)/Tao_rise )  ) + np.random.normal(size = len(T))   
