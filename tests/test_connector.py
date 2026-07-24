import numpy as np

from ComponentClasses import Connector

def test_matched_connector_halves_open_circuit_voltage():

    time_array = np.array([0.0, 1.0, 2.0])
    open_circuit_voltage = np.array([0.0, 2.0, 0.0])

    returned_time, loaded_voltage = Connector.connect(
        time_array=time_array,
        open_circuit_voltage_array=open_circuit_voltage,
        source_impedance=50.0,
        load_impedance=50.0,
    )

    np.testing.assert_array_equal(returned_time, time_array)
    np.testing.assert_allclose(loaded_voltage, [0.0, 1.0, 0.0])