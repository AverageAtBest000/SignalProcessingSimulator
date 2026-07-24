import numpy as np
from ComponentClasses import Amplifier, Connector, Digitizer


def test_known_signal_chain():
    time = np.arange(3.0)
    source = np.array([0.0, 1.0, 0.0])
    amplifier = Amplifier(2, "unitless", 50, 50, 0, 2)
    digitizer = Digitizer(50)

    _, amplifier_input = Connector.connect(time, source, 50, 50)
    _, amplifier_output = amplifier.amplify(time, amplifier_input, 0)
    _, digitizer_input = Connector.connect(time, amplifier_output, 50, 50)
    _, codes, reconstructed, _ = Digitizer.digitize(
        time, digitizer_input, 1, 2, 0, 2
    )

    np.testing.assert_array_equal(codes, [0, 1, 0])
    np.testing.assert_allclose(reconstructed, [0.25, 0.75, 0.25])