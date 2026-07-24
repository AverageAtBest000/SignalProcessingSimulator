import numpy as np
import pytest
from ComponentClasses import Generator


def test_normalized_pulse():
    time = np.linspace(-10e-9, 300e-9, 20_001)
    pulse = Generator.normalized_double_exponential(time, 0, 20e-9, 5e-9)
    assert np.all(pulse[time < 0] == 0)
    assert np.trapezoid(pulse, time) == pytest.approx(1, rel=1e-5)


def test_seed_and_polarity():
    time = np.linspace(0, 200e-9, 2001)

    positive = Generator().get_PMT_signal(polarity=1,         
                                          expected_photoelectrons=100,
                                          time_array=time,
                                          t_0=10e-9,
                                          Tao_fall=20e-9,
                                          Tao_rise=5e-9,
                                          Tao_fall_spe=6e-9,
                                          Tao_rise_spe=2e-9,
                                          relative_gain_sigma=0,
                                          random_seed=7
                                          )
    negative = Generator().get_PMT_signal(polarity=-1,
                                          expected_photoelectrons=100,
                                          time_array=time,
                                          t_0=10e-9,
                                          Tao_fall=20e-9,
                                          Tao_rise=5e-9,
                                          Tao_fall_spe=6e-9,
                                          Tao_rise_spe=2e-9,
                                          relative_gain_sigma=0,
                                          random_seed=7
                                          )
    assert np.any(positive > 0)
    np.testing.assert_array_equal(negative, -positive)