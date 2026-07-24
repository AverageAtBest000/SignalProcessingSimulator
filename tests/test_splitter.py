import numpy as np
import pytest
from ComponentClasses import Splitter

def test_symmetric_split():

    result = Splitter(10, 10, 10).split( np.arange(3.0), np.array([0.0, 2.0, 0.0]), 50, 50, 50)
    
    np.testing.assert_allclose(result[1], [0, 1, 0])
    np.testing.assert_allclose(result[3], [0, 1, 0])
    
    assert result[2] == result[4] == pytest.approx(40)