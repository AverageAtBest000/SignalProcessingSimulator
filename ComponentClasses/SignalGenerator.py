import string

import numpy as np
import scipy.constants as constants
from typing_extensions import deprecated

class Generator: 
    
    """============ Methods for simulation of PMT signal with scintillator=============="""


    def __init__(self, output_impedance = 50.0):
        self.output_impedance = output_impedance

    @classmethod
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


    def convert_to_open_circuit_pulse_area(self, measured_pulse_area, measurement_impedance):
        return measured_pulse_area * ( (self.output_impedance + measurement_impedance) / measurement_impedance)


    def get_PMT_signal( 
        self, 
        expected_photoelectrons: int, 
        time_array: np.ndarray, 
        t_0: float, 
        Tao_fall: float, 
        Tao_rise: float, 
        Tao_fall_spe: float, 
        Tao_rise_spe: float, 
        polarity: int, 
        SPE_pulse_area: float = 8.0e-12, 
        relative_gain_sigma: float = 0.2,
        random_seed: int = None,
        pulse_area_method: str = "direct",
        terminator_resistance: float = None,
        PMT_gain: float = None,
        SPE_pulse_area_is_open_circuit: bool = False,
        measurement_impedance: float = None
    ) -> np.ndarray:

        num_samples = len(time_array)
        dt = time_array[1] - time_array[0]
        
        signal = np.zeros(num_samples)

        rng = np.random.default_rng(random_seed)
        
        expected = self.get_arrival_rate(expected_photoelectrons, self.normalized_double_exponential(time_array, t_0, 
                                                                                                   Tao_fall, Tao_rise))
        expected = np.clip(expected, 0, None) * dt
        photoelectron_arrivals = rng.poisson(lam=expected, size=len(expected))
        
        pulse_area = self.set_pulse_area(method = pulse_area_method, SPE_pulse_area = SPE_pulse_area, termination_resistance = terminator_resistance, PMT_gain = PMT_gain)        
        

        if not SPE_pulse_area_is_open_circuit:
           
           if measurement_impedance is None:
               
               if pulse_area_method.lower() == "estimate_from_g_r":
                   measurement_impedance = terminator_resistance
               else:
                   measurement_impedance = 50.0
           
           pulse_area = self.convert_to_open_circuit_pulse_area( measured_pulse_area=pulse_area, measurement_impedance=measurement_impedance)


        #for every time step
        for i in range(len(photoelectron_arrivals)):
            
            #for every photon that arrived in that time step
            for photoelectron in range(photoelectron_arrivals[i]):

                relative_gain = np.clip(rng.normal(1.0, relative_gain_sigma), 0, a_max=None)
                photoelectron_time = time_array[i]

                signal += self.get_photoelectron_voltage(
                    polarity = polarity,
                    SPE_pulse_area = pulse_area,
                    relative_gain = relative_gain,
                    double_exponential_SPE = ( self.normalized_double_exponential(
                                                    time_array=time_array,
                                                    t_0=photoelectron_time,
                                                    Tao_fall=Tao_fall_spe,
                                                    Tao_rise=Tao_rise_spe
                                                    )
                    )
                )

        return signal            

        
