import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

class Generator: 
    
    @classmethod
    def get_double_exponential(cls, A, T, t_0, Tao_fall, Tao_rise):
        raw_wave =  A * ( np.exp(-(T-t_0)/Tao_fall) - np.exp( -(T-t_0)/Tao_rise )  )
        return np.where(T >= t_0, raw_wave, 0)
    
    @classmethod
    def get_PMT_signal(cls, A, T, t_0, Tao_fall, Tao_rise, Tao_fall_spe, Tao_rise_spe):
        
        num_samples = len(T)
        dt = T[1] - T[0]
        
        signal = np.zeros(num_samples)
        rng = np.random.default_rng()
        
        expected = cls.get_double_exponential(A, T, t_0, Tao_fall, Tao_rise)
        expected = np.clip(expected, 0, None) * dt
        
        arrival_noise = stats.poisson.rvs(expected, size = len(expected))    
        
        # for every time step
        for i in range(len(arrival_noise)):
            
            #for every photon that arrived in that time step
            for j in range(arrival_noise[i]):
                A_j = rng.normal(1.0, 0.2)
                t_j = T[i]
                signal += cls.get_double_exponential(A_j, T, t_j , Tao_fall_spe, Tao_rise_spe)
        
        return signal
        
