import numpy as np
from ComponentClasses import Digitizer


def test_two_bit_digitization():
    
    time_array = np.array([0.0, 1.0, 2.0])
    voltage_array = np.array([-1.0, 0.0, 1.0])

    times, codes, reconstructed, was_clipped = Digitizer.digitize( time_array=time_array, voltage_array=voltage_array, 
                                                                   sampling_rate_Hz=1.0, num_bits=2, 
                                                                   min_volts=-1.0, max_volts=1.0,)

    np.testing.assert_allclose(times, time_array)
    np.testing.assert_array_equal(codes, [0, 2, 3])
    np.testing.assert_allclose(reconstructed, [-0.75, 0.25, 0.75])
    np.testing.assert_array_equal(was_clipped, [False, False, False])