import unittest
import os
import numpy as np

import radarSignalAnalyzer.src.common as common
import radarSignalAnalyzer.src.signal_base as sb
import radarSignalAnalyzer.src.signal_processor.signal_processor as sign_proc


CONFIG = """<?xml version="1.0" ?>
<parameters>
    <logDirectory>products/outputDir</logDirectory>
    <signalParameters>
        <centralFrecuency>2434E6</centralFrecuency>
        <bandwidth>290E6</bandwidth>
    </signalParameters>
    <antennaMeasurements>
        <txPower unit="dB">11.87</txPower>
        <rxPower unit="dB">-21.91</rxPower>
        <distance unit="m">1.427</distance>
        <antennaDelay unit="s">0</antennaDelay>
    </antennaMeasurements>
    <radarMeasurements>
        <rfLosses unit="dB">-5</rfLosses>
        <cableLosses unit="dB">-1.06392</cableLosses>
        <lnaGain unit="dB">14</lnaGain>
        <mixerGain unit="dB">-5.5</mixerGain>
        <lpfGain unit="dB">9</lpfGain>
        <radarToMicGain unit="">0.6666</radarToMicGain>
        <rxLength unit="m">0.0</rxLength>
        <cableLength unit="m">0.0</cableLength>
        <propagationVel unit="">0.66667</propagationVel>
    </radarMeasurements>
    <minFreqToMeasure>250</minFreqToMeasure>
    <maxFreqToMeasure>800</maxFreqToMeasure>
    <samplesToCut>0</samplesToCut>
</parameters>
"""


class RadarReceptorTestCase(unittest.TestCase):

    def setUp(self):
        self.config_path = 'config_path'
        with open(self.config_path, 'w') as f:
            f.write(CONFIG)

        self.signal_processor = sign_proc.SignalProcessor(self.config_path)

    def test_calculating_gain_to_target_correctly(self):
        self.assertEqual(self.signal_processor.calculate_gain_to_target(1), -21.984197280441926)
        self.assertEqual(self.signal_processor.calculate_gain_to_target(0), float('inf'))

    def test_retrieving_the_peak_frequency_correctly(self):
        f = 402
        signal = sb.Signal(self.__generate_sin_wave(f))
        self.signal_processor.process_signal(signal, signal.length)

        self.assertEqual(self.signal_processor.get_processed_frequency()[1], f)

    def test_retrieving_the_distance_correctly(self):
        f = 402
        signal = sb.Signal(self.__generate_sin_wave(f))
        distance = signal.period * f / common.BW * common.C/2
        d_distance = 0.516883548275862
        self.signal_processor.process_signal(signal, signal.length)

        self.assertEqual(self.signal_processor.get_processed_distance(), (distance, d_distance))

    def test_retrieving_the_target_properties_correctly(self):
        f = 402
        signal = sb.Signal(self.__generate_sin_wave(f))
        distance = signal.period * f / common.BW * common.C/2

        self.signal_processor.process_signal(signal, signal.length)
        gain, tg_phase, rtt_ph = self.signal_processor.calculate_target_properties_from_distance(signal, distance)
        self.assertEqual(gain, 115.66890348941621)
        self.assertEqual(tg_phase, -2.768071169938505)
        self.assertEqual(rtt_ph, 1.1972748431435924)

    def __generate_sin_wave(self, frequency, duration=1, fs=common.Sampling_rate):
        """
        Generate a sin wave.
        
        :param frequency: sine frequency in Hz.
        :param duration: time in seconds.
        :param fs: frequency sampling in Hz (default 44100).
        """
        return np.sin(2*np.pi*frequency*np.arange(fs*duration)/fs)

    def tearDown(self):
        os.remove(self.config_path)
