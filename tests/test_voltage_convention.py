import unittest

import numpy as np

from ComponentClasses import Amplifier, Cable, Digitizer, EdgeDiscriminator, Generator, Splitter


class VoltageConventionTests(unittest.TestCase):

    def test_pmt_signal_is_negative_going_from_its_baseline(self):
        time_array = np.linspace(0, 100e-9, 1001)
        baseline_voltage = 0.05

        voltage_array = Generator.get_PMT_signal(
            expected_photoelectrons=100,
            time_array=time_array,
            t_0=10e-9,
            Tao_fall=2.1e-9,
            Tao_rise=0.9e-9,
            Tao_fall_spe=6e-9,
            Tao_rise_spe=2e-9,
            random_seed=4,
            baseline_voltage=baseline_voltage
        )

        self.assertTrue(np.all(voltage_array <= baseline_voltage))
        self.assertLess(np.min(voltage_array), baseline_voltage)

    def test_pulse_area_is_a_magnitude_and_polarity_sets_direction(self):
        pulse_shape = np.array([0.0, 1.0, 0.0])

        negative_pulse = Generator.get_photoelectron_voltage(-1, 0.2, 1.0, pulse_shape)

        np.testing.assert_array_equal(negative_pulse, np.array([0.0, -0.2, 0.0]))
        with self.assertRaises(ValueError):
            Generator.get_photoelectron_voltage(-1, -0.2, 1.0, pulse_shape)

    def test_splitter_preserves_baseline_and_pulse_sign(self):
        time_array = np.arange(4, dtype=float)
        baseline_voltage = 0.05
        voltage_array = np.array([0.05, 0.04, 0.03, 0.05])

        _, output_1, output_2 = Splitter(16.5, 16.5, 16.5).split(
            time_array,
            voltage_array,
            load_1_impedance=50,
            load_2_impedance=50,
            source_impedance=50,
            signal_baseline=baseline_voltage
        )

        self.assertEqual(output_1[0], baseline_voltage)
        self.assertEqual(output_2[0], baseline_voltage)
        self.assertTrue(np.all(output_1 <= baseline_voltage))
        self.assertTrue(np.all(output_2 <= baseline_voltage))

    def test_positive_amplifier_gain_preserves_negative_polarity(self):
        time_array = np.array([0.0, 1.0, 2.0])
        voltage_array = np.array([0.0, -0.1, 0.0])
        amplifier = Amplifier(2.0, "unitless", 50, 50, -1.0, 1.0)

        _, amplified_voltage = amplifier.amplify(time_array, voltage_array, signal_baseline=0.0)

        np.testing.assert_array_equal(amplified_voltage, np.array([0.0, -0.2, 0.0]))

    def test_cable_preserves_baseline_and_negative_polarity(self):
        time_array = np.array([0.0, 1.0, 2.0])
        voltage_array = np.array([0.05, -0.05, 0.05])
        cable = Cable(50, 0, 1.0, 0.0)

        _, output_voltage = cable.propagation(
            time_array,
            voltage_array,
            source_impedance=50,
            load_impedance=50,
            signal_baseline=0.05,
            max_round_trips=1
        )

        self.assertEqual(output_voltage[0], 0.05)
        self.assertLess(output_voltage[1], 0.05)

    def test_digitizer_uses_signed_voltage_range(self):
        time_array = np.array([0.0, 1.0, 2.0])
        voltage_array = np.array([-0.75, 0.0, 0.75])

        _, digitized, reconstructed, was_clipped = Digitizer.digitize(
            time_array,
            voltage_array,
            sampling_rate_Hz=1.0,
            num_bits=2,
            min_volts=-1.0,
            max_volts=1.0
        )

        np.testing.assert_array_equal(digitized, np.array([0, 2, 3]))
        self.assertTrue(np.all(np.diff(reconstructed) > 0))
        self.assertFalse(np.any(was_clipped))

    def test_negative_discriminator_uses_a_negative_threshold(self):
        time_array = np.arange(5, dtype=float)
        voltage_array = np.array([0.0, -0.1, -0.3, -0.1, 0.0])

        lead_indices, _, trail_indices, _ = EdgeDiscriminator(-0.2, -1).apply(time_array, voltage_array)

        np.testing.assert_array_equal(lead_indices, np.array([2]))
        np.testing.assert_array_equal(trail_indices, np.array([3]))


if __name__ == "__main__":
    unittest.main()
