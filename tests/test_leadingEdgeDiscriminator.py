import numpy as np
from ComponentClasses import EdgeDiscriminator


def test_positive_edge_crossings():
    
    time_array = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    voltage_array = np.array([0.0, 2.0, 2.0, 0.0, 0.0])

    discriminator = EdgeDiscriminator( threshold=1.0, polarity=1, input_impedance=50.0,)

    lead_indices, lead_times, trail_indices, trail_times =  discriminator.apply(time_array, voltage_array)

    np.testing.assert_array_equal(lead_indices, [1])
    np.testing.assert_allclose(lead_times, [0.5])
    np.testing.assert_array_equal(trail_indices, [3])
    np.testing.assert_allclose(trail_times, [2.5])