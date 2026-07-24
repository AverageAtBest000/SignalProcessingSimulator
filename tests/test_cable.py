import numpy as np
import pytest
from scipy.constants import speed_of_light
from ComponentClasses import Cable


@pytest.fixture
def lossless_cable():
    return Cable( length_m=speed_of_light * 1e-9, velocity_factor=1.0, attenuation_db_per_m=0.0, characteristic_impedance=50.0,)


def test_cable_delay(lossless_cable):
    assert lossless_cable.calculate_delay() == pytest.approx(1e-9)


@pytest.mark.parametrize( "termination_impedance, expected_coefficient", [
                            (50.0, 0.0),       
                            (0.0, -1.0),       
                            (np.inf, 1.0),     
                            (100.0, 1.0 / 3.0),
                            ],
                        )

def test_reflection_coefficient( lossless_cable, termination_impedance, expected_coefficient):
    
    result = lossless_cable.get_reflection_coefficient( termination_impedance )
    assert result == pytest.approx(expected_coefficient)


def test_attenuation_conversion():
    
    cable = Cable( length_m=2.0, velocity_factor=0.8, attenuation_db_per_m=3.0,)
    expected = 10 ** (-6.0 / 20.0)

    assert cable.get_attenuation() == pytest.approx(expected)