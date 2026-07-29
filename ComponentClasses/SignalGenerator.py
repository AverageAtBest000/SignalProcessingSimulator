import string

import numpy as np
import scipy.constants as constants
from typing_extensions import deprecated

class Generator: 
    
    


    def __init__(self, output_impedance = 50.0):
        self.output_impedance = output_impedance

    """============ Methods for simulation of PMT signal with scintillator=============="""
    
    
    @classmethod
    @deprecated("use normalized_double_exponential(), get_arival_rate() instead")
    def get_double_exponential(cls, num_photoelectrons, T, t_0, Tau_fall, Tau_rise):
        raw_wave =  num_photoelectrons / (Tau_fall - Tau_rise) * ( np.exp(-(T-t_0)/Tau_fall) - np.exp( -(T-t_0)/Tau_rise )  )
        return np.where(T >= t_0, raw_wave, 0)
    
    @classmethod
    def normalized_double_exponential(cls, time_array, t_0, Tau_fall, Tau_rise): 
        raw_wave =  ( np.exp( -(time_array-t_0) / Tau_fall) - np.exp( -(time_array - t_0) / Tau_rise )  ) / (Tau_fall - Tau_rise)
        return np.where(time_array >= t_0, raw_wave, 0)

    @classmethod
    def get_arrival_rate(cls, mean_number_photoelectrons, scintillator_double_exponential ):
        return mean_number_photoelectrons * scintillator_double_exponential
                
    @classmethod
    def get_arrival_rate_peak(cls, peak_voltage, scintillator_double_exponential):
        
        max = np.max(scintillator_double_exponential)
        max_normalized_exponential = scintillator_double_exponential / max

        return peak_voltage * max_normalized_exponential

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
        Tau_fall: float, 
        Tau_rise: float, 
        Tau_fall_spe: float, 
        Tau_rise_spe: float, 
        polarity: int, 
        SPE_pulse_area: float = 8.0e-12, 
        relative_gain_sigma: float = 0.2,
        transit_time_spread_fwhm = 0.0,
        random_seed: int = None,
        pulse_area_method: str = "direct",
        terminator_resistance: float = None,
        PMT_gain: float = None,
        SPE_pulse_area_is_open_circuit: bool = False,
        measurement_impedance: float = None
    ) -> np.ndarray:


     
        """
        Apply the load of a component the to the open circut voltage of the preceding component 
        
        Args:
            expected_photoelectrons (int): mean number of photoelectrons expected to reach the photocathode 
            time_array (np.ndarray): Array of signal's time values in seconds.
            t_0 (float): Time at which the pulse begins 
            Tau_fall (float): Constant that controls the decay time of the scintillator double exponential. A larger value will make the signal take longer to decay.
            Tau_rise (float): Constant that controls the rise time of the scintillator double exponential. A larger value will make the signal take longer to reach its peak. 
            Tau_fall_spe (float): Constant that controls the decay time of the double exponential of a single photoelectron. A larger value will make the signal take longer to decay.
            Tau_rise_spe (float): Constant that controls the rise time of the double exponential of a single photoelectron. A larger value will make the signal take longer to reach its peak.
            polarity (int): Polarity of the signal (1 or -1)
            SPE_pulse_area (float): The area under the curve of a single photo-electron pulse 
            relative_gain_sigma (float): Standard deviation of photoelctron signal intensity.
            transit_time_spread_fwhm (float): Variation in time it takes photoelectrons to reach the anode of the PMT after entering the tube. 
            random_seed (int): Seed used to generate samples from probability spreads (posson and uniform)
            pulse_area_method (str): Method for calculating pulse area under a photo-electron signal. May be "direct" or "estimate_from_g_r, which estimates using the PMT's gain and termination resistance"
            terminator_resistance (float): Optional parameter descrinbing the resistance of the resistor used to estimate the SPE pulse area
            PMT_gain (float): Optional parameter used if pulse area is estimated instead of passed in directly 
            SPE_pulse_area_is_open_circuit (bool): Optional parameter  
            measurement_impedance
        Return:
            time_array (np.ndarray): original time array.
            loaded_voltage_array (np.ndarray): Array of voltage values after the load has been applied

        """
    

        num_samples = len(time_array)
        dt = time_array[1] - time_array[0]
        
        signal = np.zeros(num_samples)

        rng = np.random.default_rng(random_seed)

        TTS_standard_dev = transit_time_spread_fwhm / 2.355
        
        expected = self.get_arrival_rate(expected_photoelectrons, self.normalized_double_exponential(time_array, t_0, 
                                                                                                   Tau_fall, Tau_rise))
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


        for i in range(len(photoelectron_arrivals)):
            
            for photoelectron in range(photoelectron_arrivals[i]):

                relative_gain = np.clip(rng.normal(1.0, relative_gain_sigma), 0, a_max=None)
                
                gaussian_offset = 0 if transit_time_spread_fwhm < 0 else rng.normal(0, TTS_standard_dev) 
                photoelectron_time = time_array[i] + gaussian_offset

                signal += self.get_photoelectron_voltage(
                    polarity = polarity,
                    SPE_pulse_area = pulse_area,
                    relative_gain = relative_gain,
                    double_exponential_SPE = ( self.normalized_double_exponential(
                                                    time_array=time_array,
                                                    t_0=photoelectron_time,
                                                    Tau_fall=Tau_fall_spe,
                                                    Tau_rise=Tau_rise_spe
                                                    )
                    )
                )

        return signal  


    def get_PMT_event_train( self, time_array : np.ndarray, 
                             event_times: np.ndarray , 
                             expected_photoelectrons: int, 
                             polarity: int,
                             Tau_fall: np.ndarray,
                             Tau_rise: np.ndarray,
                             Tau_fall_spe: np.ndarray,
                             Tau_rise_spe: np.ndarray,
                             random_seeds: np.ndarray = np.array([None, None, None ]),
                             pulse_area_method : str = "direct",
                             terminator_resistance: float = None,
                             PMT_gain: float = None,
                             SPE_pulse_area_is_open_circuit: bool = False,
                             measurement_impedance: float = None
                            ) -> np.ndarray:
        
        waveform = np.zeros(len(time_array))

        count = 0
        for event_time in event_times:

            current_wave = self.get_PMT_signal( expected_photoelectrons = expected_photoelectrons,
                                                time_array = time_array, 
                                                t_0 = event_time,
                                                polarity = polarity,
                                                Tau_fall = Tau_fall[count],
                                                Tau_rise = Tau_rise[count],
                                                Tau_fall_spe = Tau_fall_spe[count] ,
                                                Tau_rise_spe = Tau_rise_spe[count],
                                                random_seed = random_seeds[count],
                                                pulse_area_method = pulse_area_method,
                                                terminator_resistance = terminator_resistance,
                                                PMT_gain = PMT_gain,
                                                SPE_pulse_area_is_open_circuit = SPE_pulse_area_is_open_circuit,
                                                measurement_impedance = measurement_impedance
                                                 )
            count += 1 
            waveform += current_wave
    
        return waveform
        
    """============ Methods for simulation of PMT signal with scintillator=============="""

    def get_gaussian_signal(self, time_array, max_amplitude, standard_deviation):
        
        return max_amplitude * ( np.exp( -(time_array) / (2* standard_deviation **2) ) )