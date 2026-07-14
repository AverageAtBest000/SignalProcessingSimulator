import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from typing_extensions import deprecated

class Generator: 
    


    """ Methods for simulation of PMT signal with scintillator"""

    @deprecated #use normalized_double_exponential(), get_arival_rate() instead
    def get_double_exponential(cls, num_photoelectrons, T, t_0, Tao_fall, Tao_rise):
        raw_wave =  num_photoelectrons / (Tao_fall - Tao_rise) * ( np.exp(-(T-t_0)/Tao_fall) - np.exp( -(T-t_0)/Tao_rise )  )
        return np.where(T >= t_0, raw_wave, 0)
    
    @classmethod
    def normalized_double_exponential(cls, T, t_0, Tao_fall, Tao_rise): 
        return  ( np.exp( -(T-t_0) / Tao_fall) - np.exp( -(T - t_0) / Tao_rise )  ) / (Tao_fall - Tao_rise)
    
    @classmethod
    def get_arrival_rate(cls, mean_number_photoelectrons, scintillator_double_exponential ):
        raw_wave =  mean_number_photoelectrons * scintillator_double_exponential
        return np.where(T >= t_0, raw_wave, 0)

    @classmethod
    def get_photoelectron_voltage(cls, T, t_j, polarity, SPE_pulse_area, relative_gain, double_exponential_SPE):
        return polarity * SPE_pulse_area * relative_gain * (T - t_j)

    @classmethod
    def get_PMT_signal(cls, num_photoelectrons, T, t_0, Tao_fall, Tao_rise, Tao_fall_spe, Tao_rise_spe):
        
        num_samples = len(T)
        dt = T[1] - T[0]
        
        signal = np.zeros(num_samples)
        rng = np.random.default_rng()
        
        expected = cls.get_double_exponential(num_photoelectrons, T, t_0, Tao_fall, Tao_rise)
        expected = np.clip(expected, 0, None) * dt
        
        arrival_noise = stats.poisson.rvs(expected, size = len(expected))    
        
        # for every time step
        for i in range(len(arrival_noise)):
            
            #for every photon that arrived in that time step
            for photoelectron in range(arrival_noise[i]):

                relative_photoelectron_gain = rng.normal(1.0, 0.2)
                t_j = T[i]
                signal += cls.get_double_exponential(relative_photoelectron_gain, T, t_j , Tao_fall_spe, Tao_rise_spe)
        
        return signal
        
