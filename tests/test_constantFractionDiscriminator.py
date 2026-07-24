import numpy as np

from ComponentClasses import ConstantFractionDiscriminator


def test_cfd_crossing_time():
    time_array = np.arange(6.0)
    voltage_array = np.array([0.0, 1.0, 2.0, 1.0, 0.0, 0.0])

    discriminator = ConstantFractionDiscriminator( attenuation=0.5, delay=1.0, 
                                                   armed_threshold=0.5, input_impedance=50.0,
    )

    crossing_indices, crossing_times = discriminator.apply( time_array=time_array, loaded_voltage_array=voltage_array, 
                                                            signal_baseline=0.0, polarity=1,)

    np.testing.assert_array_equal(crossing_indices, [2])
    np.testing.assert_allclose(crossing_times, [2.0])