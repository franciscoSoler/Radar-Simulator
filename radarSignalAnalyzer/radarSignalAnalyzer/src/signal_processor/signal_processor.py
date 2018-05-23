import numpy as np
import logging

import radarSignalAnalyzer.src.utils.gaussian_calculator as gc
import radarSignalAnalyzer.src.utils.config_file_manager as cfm
import radarSignalAnalyzer.src.signal_processor as sp
import radarSignalAnalyzer.src.common as common


class SignalProcessor:

    def __init__(self, config_path):
        self.__logger = logging.getLogger(__name__)
        self.__subtract_medium_phase = True
        self.__rf_chain_gain = None
        self.__cable_phase = None
        self.__componens_delay = None
        self.__freq_cut = 0

        self.__frequency = None
        self.__d_f = 0
        self.__distance = 0
        self.__d_r = 0

        self.__initialize(config_path)

    def __initialize(self, config_path):
        """Calculate the cable phase, component's delay and rf chain gain from the measurements."""
        manager = cfm.ConfigFileManager(config_path)
        wavelength = common.C / manager.get_parameter(cfm.ConfTags.F0)
        dist_loss = common.v2db(4*np.pi*manager.get_parameter(cfm.ConfTags.DIST)/wavelength)
        gt_gr = manager.get_parameter(cfm.ConfTags.RXPW) - manager.get_parameter(cfm.ConfTags.TXPW) + dist_loss
        self.__rf_chain_gain = manager.get_parameter(cfm.ConfTags.TXPW) + gt_gr + \
            2*manager.get_parameter(cfm.ConfTags.CABL) + manager.get_parameter(cfm.ConfTags.RFL) + \
            manager.get_parameter(cfm.ConfTags.LNAG) + manager.get_parameter(cfm.ConfTags.MIXG) + \
            manager.get_parameter(cfm.ConfTags.LPFG) + common.v2db(manager.get_parameter(cfm.ConfTags.R2MG))

        cable_vel = common.C * manager.get_parameter(cfm.ConfTags.PROP)
        cable_delay = manager.get_parameter(cfm.ConfTags.CABLN)/cable_vel

        self.__cable_phase = common.format_phase(cable_delay*manager.get_parameter(cfm.ConfTags.F0)*360)

        rx_delay = manager.get_parameter(cfm.ConfTags.RXLN)/cable_vel
        self.__componens_delay = 2 * (manager.get_parameter(cfm.ConfTags.DELAY) + cable_delay) + rx_delay
        self.__freq_cut = manager.get_parameter(cfm.ConfTags.MINFREQ)

        self.__logger.info('Calculated gain of the RF chain: %f', self.__rf_chain_gain)
        self.__logger.info('Calculated phase of cables: %f', self.__cable_phase)
        self.__logger.info('Calculated components delay: %f', self.__componens_delay)

    def __calculate_distance(self, signal, freq_points):
        """
        Calculate the distance between the target and the radar with its resolution.

        :param signal: the received signal with the radar.
        :param freq_points: the amount of points used to do the fft.
        """
        self.__distance = (signal.period * self.__d_f / signal.bandwidth - self.__componens_delay) * common.C/2
        self.__d_r = common.C/2/signal.bandwidth * signal.length/freq_points

    def __calculate_frequency(self, signal, freq_points):
        """
        Calculate the frequency related to the distance between the target and the radar with its resolution.

        :param signal: the received signal with the radar.
        :param freq_points: the amount of points used to do the fft.
        """
        self.__frequency, freq_sampling = signal.obtain_spectrum(freq_points)
        f_min = self.__freq_cut*freq_points//freq_sampling
        self.__d_f = (f_min+np.argmax(abs(self.__frequency[int(f_min):])))*freq_sampling/freq_points

    def process_signal(self, signal, freq_points):
        """
        Process the received signal in order to obtain the distance between the target and the radar.

        :param signal: the received signal with the radar.
        :param freq_points: the amount of points used to do the fft.
        """
        self.__calculate_frequency(signal, freq_points)
        self.__calculate_distance(signal, freq_points)

    def calculate_target_properties_from_distance(self, signal, distance):
        gain = common.w2db(2*signal.power * (4*np.pi)**3 * distance**4 / signal.wavelength**2) - self.__rf_chain_gain

        # This part is for calculating the distances phase shift
        k = 2*np.pi*signal.bandwidth/signal.period
        tau = 2*distance / common.C
        wc = 2*np.pi*signal.central_freq

        antenna_phase = 2 * 192.15

        rtt_ph = common.format_phase(wc*tau - k*tau*signal.period/2 - k*tau**2/2 + 2*self.__cable_phase + antenna_phase)
        ang = np.angle(self.__frequency)[np.argmax(abs(self.__frequency))]

        return gain, common.format_phase(ang - rtt_ph if self.__subtract_medium_phase else ang), rtt_ph

    @staticmethod
    def calculate_gain_to_target(distance):
        """Calculate the gain to target in dBs."""
        return common.w2db(1/(np.power(4*np.pi, 2) * distance**4) if distance else float("inf"))

    def get_processed_frequency(self):
        return self.__frequency, self.__d_f

    def get_processed_distance(self):
        return self.__distance, self.__d_r
