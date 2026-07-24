import numpy as np
import pytest
from ComponentClasses import Amplifier


def test_gain_baselines_and_clipping():
    amplifier = Amplifier(2, "unitless", 50, 50, -1, 1)
    _, output = amplifier.amplify( np.arange(3.0), np.array([0.2, 0.7, -0.8]), 0.2, -0.1)
    np.testing.assert_allclose(output, [-0.1, 0.9, -1.0])


def test_db_gain():
    assert Amplifier(20, "db", 50, 50, -100, 100).gain == pytest.approx(10)


def test_filter_dc_response():
    voltage = np.ones(5)
    np.testing.assert_allclose( Amplifier.apply_high_freq_cutoff(voltage, 1, 0.1), voltage)
    np.testing.assert_allclose( Amplifier.apply_low_freq_cutoff(voltage, 1, 0.1), 0, atol=1e-15)