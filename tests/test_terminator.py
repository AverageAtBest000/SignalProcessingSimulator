import numpy as np
import pytest

from ComponentClasses import Cable, Terminator


@pytest.mark.parametrize("impedance, scale", [(50, 0.5), (np.inf, 1), (0, 0)])
def test_termination_voltage(impedance, scale):
    
    cable = Cable(0, 1, 0, 50)
    _, output = Terminator(impedance).apply_reflection( cable, np.arange(3.0), np.array([0.0, 2.0, 0.0]), 50, 0, 1)
    
    np.testing.assert_allclose(output, [0, 2 * scale, 0])