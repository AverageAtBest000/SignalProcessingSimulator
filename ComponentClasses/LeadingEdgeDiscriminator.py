import numpy as np

class EdgeDiscriminator:

    def __init__(self, threshold: float, polarity: int, input_impedance: float):
        self.threshold = threshold
        self.polarity = polarity
        self.input_impedance = input_impedance

    def apply(self, time_array: np.ndarray, signal_array: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:

        if self.polarity == -1 :
            threshhold_is_a = signal_array <= self.threshold
        else:
            threshhold_is_a = signal_array >= self.threshold

        transitions = np.diff(threshhold_is_a.astype(int), prepend = 0)

        lead_indices = np.where(transitions == 1)[0] 
        trail_indices = np.where(transitions == -1)[0] 

        lead_times = self.interpolate_crossing_times( time_array, signal_array, lead_indices)
        trail_times = self.interpolate_crossing_times( time_array, signal_array, trail_indices)

        return lead_indices, lead_times, trail_indices, trail_times

        
    def interpolate_crossing_times(self, time_array, signal_array, indices):

        crossing_times = []

        for index in indices:
            
            if index == 0:
                crossing_times.append(time_array[0])
            else:
                previous_index = index - 1
                voltage_change = signal_array[index] - signal_array[previous_index]
                crossing_fraction = (self.threshold - signal_array[previous_index]) / voltage_change
                crossing_time = time_array[previous_index] + crossing_fraction * ( time_array[index] - time_array[previous_index] )
                crossing_times.append(crossing_time)

        return np.array(crossing_times)
