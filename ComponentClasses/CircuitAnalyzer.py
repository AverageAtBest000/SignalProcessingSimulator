import numpy as np
from scipy import signal


class CircuitAnalyzer:

    def __init__(self,
                       low_fraction=0.1, 
                       high_fraction=0.9,
                       delay_method="correlation"):
        
        self.low_fraction = low_fraction
        self.high_fraction = high_fraction
        self.delay_method = delay_method
        self.stages = {}

    def record_stage( self, name, time_array, 
                            voltage_array, polarity,
                            component_name = None, voltage_type = None, 
                            baseline = None, baseline_window = None, 
                            integration_window = None, source_impedance = None, 
                            load_impedance = None, characteristic_impedance = None, 
                            adc_codes = None, was_clipped = None, 
                            notes = None
                            ):

        self.validate_stage(time_array, voltage_array, polarity)

        reflection_info = None
        
        if characteristic_impedance is not None and load_impedance is not None:
            reflection_info = self.get_reflection_info(characteristic_impedance, load_impedance, source_impedance)

        measurements = self.analyze_wave(time_array, voltage_array,
                                         polarity, baseline,
                                         baseline_window, integration_window)

        self.stages[name] = {
            "name": name,
            "component_name": component_name,
            "voltage_type": voltage_type,
            "time_array": time_array,
            "voltage_array": voltage_array,
            "polarity": polarity,
            "baseline_window": baseline_window,
            "integration_window": integration_window,
            "source_impedance_ohms": source_impedance,
            "load_impedance_ohms": load_impedance,
            "characteristic_impedance_ohms": characteristic_impedance,
            "measurements": measurements,
            "reflection_information": reflection_info,
            "digitizer_information": self.analyze_digitizer( adc_codes, was_clipped),
            "notes": notes,
        }
        return self.stages[name]

    def validate_stage(self, time_array, voltage_array, polarity):
        if len(time_array) != len(voltage_array):
            raise ValueError("time_array and voltage_array must be of equal length")
        if not 0 <= self.low_fraction < self.high_fraction <= 1:
            raise ValueError("fractions must satisfy 0 <= low < high <= 1")
        if polarity != 1 and polarity != -1:
            raise ValueError("polarity must either be 1 or -1")
    
    def display_diagnostics(self, stage_name):

        stage = self.stages[stage_name]
    
        print(f"\nDiagnostics for {stage_name}")
    
        for section in (
            "measurements",
            "reflection_information",
            "digitizer_information",
        ):
            diagnostics = stage[section]
    
            if diagnostics is not None:
                print(f"\n{section.replace('_', ' ').title()}")
    
                for name, value in diagnostics.items():
                    print(f"{name}: {value}")

    @classmethod
    def get_reflection_info( cls, 
                             characteristic_impedance, load_impedance, 
                             source_impedance = None):

        load_reflection = cls.get_reflection_coefficient(load_impedance, characteristic_impedance)
        source_reflection = None

        if source_impedance is None:
            source_reflection = cls.get_reflection_coefficient(source_impedance, characteristic_impedance)
        
        abs_reflection = np.abs(load_reflection)
        reflected_power_fraction = abs_reflection ** 2

        if abs_reflection == 0:
            return_loss_db = np.inf
            voltage_standing_wave_ratio = 1.0
        elif abs_reflection >= 1:
            return_loss_db = 0.0
            voltage_standing_wave_ratio = np.inf
        else:
            return_loss_db = -20 * np.log10(abs_reflection)
            voltage_standing_wave_ratio = 1 + abs_reflection / (1 - abs_reflection)


        return {
                "load_reflection_coefficient" : load_reflection,
                "source_reflection_coefficient" : source_reflection,
                "reflected_voltage_fraction" : abs_reflection,
                "reflected_power_fraction" : reflected_power_fraction,
                "load_voltage_transmission_coefficient" : 1 + load_reflection,
                "return_loss_db" : return_loss_db,
                "voltage_standing_wave_ratio" : voltage_standing_wave_ratio
               }           


    def calculate_delay(self, reference, output):

        if self.delay_method == "peak":
            return output["measurements"]["peak_time_seconds"] - reference["measurements"]["peak_time_seconds"]
            
        if self.delay_method != "correlation":
            raise ValueError( 'delay_method must be "peak" or "correlation"')

        reference_time = reference["time_array"]
        reference_voltage = self.get_oriented_voltage(reference)

        output_voltage = np.interp( reference_time, output["time_array"], self.get_oriented_voltage(output), left=0.0, right=0.0)

        reference_voltage = reference_voltage - np.mean(reference_voltage)
        output_voltage = output_voltage - np.mean(output_voltage)

        correlation_values = signal.correlate( output_voltage, reference_voltage, mode="full", method="fft")

        lags = signal.correlation_lags( len(output_voltage), len(reference_voltage), mode="full")

        lag = lags[np.argmax(correlation_values)]
        sample_period = np.median(np.diff(reference_time))
        
        return lag * sample_period

    @classmethod
    def analyze_digitizer(cls, adc_codes=None, was_clipped=None):
        
        if adc_codes is None and was_clipped is None:
            return None

        data = {
            "minimum_adc_code": None,
            "maximum_adc_code": None,
            "clipped_sample_count": None,
            "clipped_fraction": None,
        }

        if adc_codes is not None:
            data["minimum_adc_code"] = np.min(adc_codes)
            data["maximum_adc_code"] = np.max(adc_codes)

        if was_clipped is not None:
            data["clipped_sample_count"] = np.sum(was_clipped)
            data["clipped_fraction"] = np.mean(was_clipped)

        return data

    @classmethod
    def get_reflection_coefficient(cls,impedance, characteristic_impedance):

        if np.isinf(impedance): 
            return 1.0
        
        return impedance - characteristic_impedance / (impedance + characteristic_impedance)


    def analyze_wave(self, time_array, voltage_array,
                           polarity, baseline = None,
                           baseline_window = None, integration_window = None):
    
        if baseline is None:
            baseline_samples = self.get_window_samples(time_array, voltage_array, baseline_window)
            baseline = np.mean(baseline_samples)
        else:
            baseline = baseline

        if baseline_window is None:
            baseline_rms = np.nan
        else:
            baseline_samples = self.get_window_samples( time_array, voltage_array, baseline_window)
            baseline_rms = np.sqrt(np.mean((baseline_samples - baseline) ** 2))

        pulse_voltage = voltage_array - baseline
        oriented_voltage = polarity * pulse_voltage

        peak_index = np.argmax(oriented_voltage)
        peak_amplitude = oriented_voltage[peak_index]

        if np.isnan(baseline_rms):
            signal_to_noise_ratio = np.nan
        elif baseline_rms == 0:
            signal_to_noise_ratio = np.inf if peak_amplitude > 0 else 0.0
        else:
            signal_to_noise_ratio = peak_amplitude / baseline_rms

        low_level = self.low_fraction * peak_amplitude
        high_level = self.high_fraction * peak_amplitude
        half_level = 0.5 * peak_amplitude


        rise_low = self.find_crossing( time_array, oriented_voltage, peak_index, low_level, "leading")
        
        rise_high = self.find_crossing( time_array, oriented_voltage, peak_index, high_level, "leading")
        
        fall_high = self.find_crossing( time_array, oriented_voltage, peak_index, high_level, "trailing")
        
        fall_low = self.find_crossing( time_array, oriented_voltage, peak_index, low_level, "trailing" )
        
        half_rise = self.find_crossing( time_array, oriented_voltage, peak_index, half_level, "leading")

        half_fall = self.find_crossing( time_array, oriented_voltage, peak_index, half_level, "trailing")

        integration_time, integration_voltage = self.get_integration_data( time_array, oriented_voltage, integration_window )

        return {
            "baseline_volts": baseline,
            "baseline_rms_volts": baseline_rms,
            "polarity": polarity,
            "peak_index": peak_index,
            "peak_time_seconds": time_array[peak_index],
            "peak_voltage_volts": voltage_array[peak_index],
            "peak_amplitude_volts": peak_amplitude,
            "pulse_area_volt_seconds": np.trapezoid(integration_voltage, integration_time), 
            "rise_time_seconds": self.subtract_times(rise_high, rise_low),
            "fall_time_seconds": self.subtract_times(fall_low, fall_high),
            "fwhm_seconds": self.subtract_times(half_fall, half_rise),
            "signal_to_noise_ratio": signal_to_noise_ratio
        }



    def compare_stages(self, reference_stage_name, output_stage_name):

        reference = self.stages[reference_stage_name]
        output = self.stages[output_stage_name]

        reference_data = reference["measurements"]
        output_data = output["measurements"]

        delay = self.calculate_delay(reference, output)

        reference_voltage = self.get_oriented_voltage(reference)

        aligned_output = np.interp( reference["time_array"] + delay, output["time_array"], self.get_oriented_voltage(output), left=np.nan, right=np.nan )

        valid_samples = np.isfinite(aligned_output)
        shape_correlation = self.calculate_correlation( reference_voltage[valid_samples], aligned_output[valid_samples] )

        peak_ratio = self.safe_ratio( output_data["peak_amplitude_volts"], reference_data["peak_amplitude_volts"])
        area_ratio = self.safe_ratio( output_data["pulse_area_volt_seconds"], reference_data["pulse_area_volt_seconds"],)

        return {
            "reference_stage": reference_stage_name,
            "output_stage": output_stage_name,
            "delay_seconds": float(delay),
            "peak_amplitude_ratio": peak_ratio,
            "peak_change_db": self.ratio_to_db(peak_ratio),
            "signal_loss_percent": self.ratio_to_loss_percent(peak_ratio),
            "pulse_area_ratio": area_ratio,
            "pulse_area_change_percent": self.ratio_to_change_percent( area_ratio ),
            "baseline_shift_volts": ( output_data["baseline_volts"] - reference_data["baseline_volts"]),
            "rise_time_change_seconds": self.subtract_times( output_data["rise_time_seconds"], reference_data["rise_time_seconds"]),
            "fall_time_change_seconds": self.subtract_times( output_data["fall_time_seconds"], reference_data["fall_time_seconds"]),
            "fwhm_change_seconds": self.subtract_times( output_data["fwhm_seconds"], reference_data["fwhm_seconds"]),
            "shape_correlation": shape_correlation
            }

    def get_report(self, reference_stage_name=None):
        report = {
            "stages": {},
            "comparisons": {},
        }

        for name, stage in self.stages.items():
            report["stages"][name] = {
                key: value
                for key, value in stage.items()
                if key not in ("time_array", "voltage_array")
            }

        if reference_stage_name is not None:
            for name in self.stages:
                if name != reference_stage_name:
                    report["comparisons"][name] = self.compare_stages(
                        reference_stage_name,
                        name,
                    )

        return report


    @classmethod
    def get_oriented_voltage(cls, stage):
        data = stage["measurements"]
        return data["polarity"] * ( stage["voltage_array"] - data["baseline_volts"])

    def calculate_delay(self, reference, output):
        if self.delay_method == "peak":
            return (
                output["measurements"]["peak_time_seconds"]
                - reference["measurements"]["peak_time_seconds"]
            )

        if self.delay_method != "correlation":
            raise ValueError(
                'delay_method must be "peak" or "correlation"'
            )

        reference_time = reference["time_array"]
        reference_voltage = self.get_oriented_voltage(reference)

        output_voltage = np.interp(
            reference_time,
            output["time_array"],
            self.get_oriented_voltage(output),
            left=0.0,
            right=0.0,
        )

        reference_voltage = reference_voltage - np.mean(reference_voltage)
        output_voltage = output_voltage - np.mean(output_voltage)

        correlation_values = signal.correlate(
            output_voltage,
            reference_voltage,
            mode="full",
            method="fft",
        )
        lags = signal.correlation_lags(
            len(output_voltage),
            len(reference_voltage),
            mode="full",
        )

        lag = int(lags[np.argmax(correlation_values)])
        sample_period = float(np.median(np.diff(reference_time)))
        return lag * sample_period
    
    @classmethod
    def get_window_samples(cls, time_array, voltage_array, window):
        
        start_time, end_time = window

        mask = (time_array >= start_time) & (time_array <= end_time)
        samples = voltage_array[mask]

        if samples.size == 0:
            raise ValueError("The selected baseline_window contains no samples" )

        return samples
        
    @classmethod
    def find_crossing(cls, time_array, voltage_array, 
                           peak_index,threshold, 
                           side ):
        if side == "leading":

            indices = range(peak_index - 1, -1, -1)
            def condition(index):
                return  voltage_array[index] <= threshold <= voltage_array[index + 1]
                
        elif side == "trailing":
            
            indices = range(peak_index, len(voltage_array) - 1)

            def condition(index):
                return  voltage_array[index] >= threshold >= voltage_array[index + 1]
                
        else:
            raise ValueError('side must be "leading" or "trailing"')

        for index in indices:

            if condition(index):
                voltage_change =  voltage_array[index + 1] - voltage_array[index]
                
                if voltage_change == 0:
                    return float(time_array[index])

                fraction = (threshold - voltage_array[index]) / voltage_change
            
                return  time_array[index] + fraction * ( time_array[index + 1] - time_array[index] )

        return np.nan 

    @classmethod
    def get_integration_data(cls, time_array, voltage_array,
                             integration_window):
        
        if integration_window is None:
            return time_array, voltage_array

        start_time, end_time = integration_window
        interior = (time_array > start_time) & (time_array < end_time)

        integration_time = np.concatenate((
            np.array([start_time]),
            time_array[interior],
            np.array([end_time]),
        ))

        integration_voltage = np.interp( integration_time, time_array, voltage_array)

        return integration_time, integration_voltage


    @classmethod
    def subtract_times(cls, later_time, earlier_time):
        return float(later_time - earlier_time)

    @classmethod
    def calculate_correlation(cls, reference_voltage, output_voltage):
        if len(reference_voltage) < 2 or len(output_voltage) < 2:
            return np.nan

        if (
            np.std(reference_voltage) == 0
            or np.std(output_voltage) == 0
        ):
            return np.nan

        return float(
            np.corrcoef(reference_voltage, output_voltage)[0, 1]
        )

    @classmethod
    def safe_ratio(cls, numerator, denominator):
        if denominator == 0:
            return np.nan
        
        return numerator / denominator

    @classmethod
    def ratio_to_db(cls, ratio):
        if not np.isfinite(ratio) or ratio <= 0:
            return np.nan

        return 20 * np.log10(ratio)

    @classmethod
    def ratio_to_loss_percent(cls, ratio):
        if not np.isfinite(ratio):
            return np.nan

        return (1 - ratio) * 100

    @classmethod
    def ratio_to_change_percent(cls, ratio):
        if not np.isfinite(ratio):
            return np.nan

        return (ratio - 1) * 100
