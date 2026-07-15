import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.constants as constants
from typing_extensions import deprecated

class Generator: 
    
    """============ Methods for simulation of PMT signal with scintillator=============="""

    @deprecated("use normalized_double_exponential(), get_arival_rate() instead")
    def get_double_exponential(cls, num_photoelectrons, T, t_0, Tao_fall, Tao_rise):
        raw_wave =  num_photoelectrons / (Tao_fall - Tao_rise) * ( np.exp(-(T-t_0)/Tao_fall) - np.exp( -(T-t_0)/Tao_rise )  )
        return np.where(T >= t_0, raw_wave, 0)
    


    @classmethod
    def normalized_double_exponential(cls, time_array, t_0, Tao_fall, Tao_rise): 
        raw_wave =  ( np.exp( -(time_array-t_0) / Tao_fall) - np.exp( -(time_array - t_0) / Tao_rise )  ) / (Tao_fall - Tao_rise)
        return np.where(time_array >= t_0, raw_wave, 0)



    @classmethod
    def get_arrival_rate(cls, mean_number_photoelectrons, scintillator_double_exponential ):
        return mean_number_photoelectrons * scintillator_double_exponential
         

                
    @classmethod
    def get_photoelectron_voltage(cls, polarity, SPE_pulse_area, relative_gain, double_exponential_SPE):
        return polarity * SPE_pulse_area * relative_gain * double_exponential_SPE 



    @classmethod
    def set_pulse_area(cls, method, SPE_pulse_area = None, PMT_gain = None, termination_resistance = None) -> float:
        
        if method.lower() == "direct" and SPE_pulse_area is not None:
                return SPE_pulse_area
        elif method.lower() == "estimate_from_g_r" and PMT_gain is not None and termination_resistance is not None:
            return termination_resistance * constants.elementary_charge * PMT_gain 
        else:
            raise ValueError("unknown method or incorrect arguments detected")



    @classmethod
    def get_PMT_signal(cls, expected_photoelectrons, time_array, t_0, Tao_fall, Tao_rise, Tao_fall_spe, Tao_rise_spe, polarity): 
        num_samples = len(time_array)
        dt = time_array[1] - time_array[0]
        
        signal = np.zeros(num_samples)
        rng = np.random.default_rng()
        
        expected = cls.get_arrival_rate(expected_photoelectrons, cls.normalized_double_exponential(time_array, t_0, 
                                                                                                   Tao_fall, Tao_rise))
        expected = np.clip(expected, 0, None) * dt
        photoelectron_arrivals = rng.poisson(lam=expected, size=len(expected))
        
        # for every time step
        for i in range(len(photoelectron_arrivals)):
            
            #for every photon that arrived in that time step
            for photoelectron in range(photoelectron_arrivals[i]):

                relative_gain = np.clip(rng.normal(1.0, 0.2))
                photoelectron_time = time_array[i]

                signal += cls.get_photoelectron_voltage( polarity = polarity, 
                                                         SPE_pulse_area = cls.set_pulse_area(method="direct", SPE_pulse_area=8.0e-12),
                                                         relative_gain = relative_gain,
                                                         double_exponential_SPE = cls.normalized_double_exponential(time_array = time_array, 
                                                                                                                     t_0 = photoelectron_time, 
                                                                                                                     Tao_fall = Tao_fall_spe, 
                                                                                                                     Tao_rise = Tao_rise_spe )
                                                        )
        return signal
        
