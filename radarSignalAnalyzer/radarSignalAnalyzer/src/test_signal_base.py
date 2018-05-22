import unittest
import os
import numpy as np

import radarSignalAnalyzer.src.common as common
import radarSignalAnalyzer.src.signal_base as sb


class RadarReceptorTestCase(unittest.TestCase):

    def setUp(self):
        self.f = 402
        self.signal = sb.Signal(self.__generate_sin_wave(self.f))
    
    def test_retrieving_the_signal_properly(self):
        sign = self.__generate_sin_wave(self.f)

        np.testing.assert_array_equal(self.signal.signal, sign)

    def test_retrieving_the_power_properly(self):
        self.assertAlmostEqual(self.signal.power, 1/2)

    def test_subtracting_two_signals(self):
        s1 = self.__generate_sin_wave(self.f)
        s2 = self.__generate_sin_wave(self.f) * 1/2
        self.signal.subtract_signals(sb.Signal(s2))

        np.testing.assert_array_equal(self.signal.signal, s1 - s2)

    def test_obtaining_peak_of_spectrum(self):
        spectrum, fs = self.signal.obtain_spectrum(self.signal.length)
        self.assertEqual(max(abs(spectrum)), 1/2)
        self.assertEqual(fs, common.Sampling_rate)

    def test_obtaining_frequency_peak_of_spectrum(self):
        spectrum, fs = self.signal.obtain_spectrum(self.signal.length)
        self.assertEqual(fs*np.array(abs(spectrum)).argmax()/self.signal.length, self.f)

    def test_cutting_the_signal(self):
        samples_to_remove = 8
        total_samples = self.signal.length
        self.signal.cut(samples_to_remove)
        self.assertEqual(self.signal.length, total_samples - samples_to_remove)

    def __generate_sin_wave(self, frequency, duration=1, fs=common.Sampling_rate):
        """
        Generate a sin wave.
        
        :param frequency: sine frequency in Hz.
        :param duration: time in seconds.
        :param fs: frequency sampling in Hz (default 44100).
        """
        return np.sin(2*np.pi*frequency*np.arange(fs*duration)/fs)

    # def tearDown(self):
        # os.remove(self.config_path)
