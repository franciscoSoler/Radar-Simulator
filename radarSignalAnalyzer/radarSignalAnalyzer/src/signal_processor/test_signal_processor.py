import unittest
import os

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
        <antennaDelay unit="s">0.31688E-9</antennaDelay>
    </antennaMeasurements>
    <radarMeasurements>
        <rfLosses unit="dB">-5</rfLosses>
        <cableLosses unit="dB">-1.06392</cableLosses>
        <lnaGain unit="dB">14</lnaGain>
        <mixerGain unit="dB">-5.5</mixerGain>
        <lpfGain unit="dB">9</lpfGain>
        <radarToMicGain unit="">0.6666</radarToMicGain>
        <rxLength unit="m">0.07</rxLength>
        <cableLength unit="m">0.365</cableLength>
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

    def tearDown(self):
        os.remove(self.config_path)
