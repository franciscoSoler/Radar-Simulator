from PyQt5 import QtCore
import numpy as np
import scipy as sp
import enum
import os

import radarSignalAnalyzer.src.utils.config_file_manager as cfm
import radarSignalAnalyzer.src.utils.gaussian_calculator as gc
import radarSignalAnalyzer.src.real_receiver as r_receiver
import radarSignalAnalyzer.src.file_receiver as f_receiver
import radarSignalAnalyzer.src.signal_processor as signal_processor
import radarSignalAnalyzer.src.distance_calculator as calculator
import radarSignalAnalyzer.src.common as common
import radarSignalAnalyzer.src.signal_base as sign

np.seterr(all='raise')


def w2db(w):
    """Converts power [W] to dBs"""
    return -99999999999 if w == 0 else 10*np.log10(w)


def v2db(v):
    """Converts voltage [V] to dBs"""
    return 2*w2db(abs(v))


def db2v(dbs):
    """Converts dBs to voltage [V]"""
    return 10**(dbs/20)


class Measurement(enum.Enum):
    Gain = 1
    Phase = 2
    Distance = 3


class Controller(QtCore.QObject):

    update_data = QtCore.pyqtSignal(float, tuple, float, tuple, tuple, float, float, float)

    def __init__(self, max_freq, real_time=True):
        super(Controller, self).__init__()
        self.__measure_clutter = False

        self.__max_freq = max_freq
        self.__receiver = None
        self.__num_samples = None
        self.__clutter = None
        self.__freq_points = None
        self.__quantity_freq_samples = None

        self.set_real_time_mode(real_time)
        self.__samples_to_cut = 0
        self.__use_external_clutter = False
        self.__ext_clutter = None
        self.__rf_chain_gain = None
        self.__cable_phase = None
        self.__componens_delay = None

        self.__freq_cut = 0
        self.__subtract_medium_phase = True
        self.__distance_from_gui = 0
        self.__use_distance_from_gui = False

        self.__measurements = {me: gc.GaussianCalculator() for me in Measurement}
        self.__cut = np.pi

        self.__initialize()

    def __initialize(self):
        """Calculate the cable phase, component's delay and rf chain gain from the measurements."""
        manager = cfm.ConfigFileManager(os.path.join(os.path.dirname(__file__), common.CONFIG_PATH))
        wavelength = common.C / manager.get_parameter(cfm.ConfTags.F0)
        dist_loss = v2db(4*np.pi*manager.get_parameter(cfm.ConfTags.DIST)/wavelength)
        gt_gr = manager.get_parameter(cfm.ConfTags.RXPW) - manager.get_parameter(cfm.ConfTags.TXPW) + dist_loss
        self.__rf_chain_gain = manager.get_parameter(cfm.ConfTags.TXPW) + gt_gr + \
            2*manager.get_parameter(cfm.ConfTags.CABL) + manager.get_parameter(cfm.ConfTags.RFL) + \
            manager.get_parameter(cfm.ConfTags.LNAG) + manager.get_parameter(cfm.ConfTags.MIXG) + \
            manager.get_parameter(cfm.ConfTags.LPFG) + v2db(manager.get_parameter(cfm.ConfTags.R2MG))

        cable_vel = common.C * manager.get_parameter(cfm.ConfTags.PROP)
        cable_delay = manager.get_parameter(cfm.ConfTags.CABLN)/cable_vel

        self.__cable_phase = signal_processor.format_phase(cable_delay*manager.get_parameter(cfm.ConfTags.F0)*360)

        rx_delay = manager.get_parameter(cfm.ConfTags.RXLN)/cable_vel
        self.__componens_delay = 2 * (manager.get_parameter(cfm.ConfTags.DELAY) + cable_delay) + rx_delay
        self.__freq_cut = manager.get_parameter(cfm.ConfTags.MINFREQ)
        self.__samples_to_cut = int(manager.get_parameter(cfm.ConfTags.SAMPCUT))

    def __initialize_singal_properties(self):
        """Align every property to the receiving signal."""
        self.__num_samples = self.__receiver.get_num_samples_per_period()

        while not self.__num_samples:
            self.__num_samples = self.__receiver.get_num_samples_per_period()

        self.__clutter = sign.Signal([0]*self.__num_samples)
        self.__freq_points = int(np.exp2(np.ceil(np.log2(self.__num_samples))+7))
        self.__quantity_freq_samples = int(self.__max_freq*self.__freq_points//self.__receiver.sampling_rate)

    @property
    def signal_length(self):
        return self.__num_samples - self.__samples_to_cut

    @property
    def freq_length(self):
        return self.__quantity_freq_samples

    def get_signal_range(self):
        d_t = 1/self.__receiver.sampling_rate
        return np.linspace(0, d_t * self.signal_length, num=self.signal_length, endpoint=False)

    def get_frequency_range(self):
        d_f = self.__receiver.sampling_rate/self.__freq_points
        return np.arange(0, (d_f*self.__freq_points)//2, d_f)[:self.__quantity_freq_samples]

    def get_disance_from_freq(self, freq):
        signal = self.__receiver.get_audio_data(self.__num_samples)
        return signal.period * freq*common.C/(2*signal.bandwidth)

    def __calculate_targets_properties(self, signal, frequency, distance):
        gain = w2db(2*signal.power * (4*np.pi)**3 * distance**4 / signal.wavelength**2) - self.__rf_chain_gain

        # This part is for calculating the distances phase shift
        k = 2*np.pi*signal.bandwidth/signal.period
        tau = 2*distance / common.C
        wc = 2*np.pi*signal.central_freq

        antenna_phase = 2 * 192.15

        rtt_ph = signal_processor.format_phase(wc*tau - k*tau*signal.period/2 - k*tau**2/2 + 2*self.__cable_phase + antenna_phase)
        ang = np.angle(frequency)[np.argmax(abs(frequency))]

        return gain, signal_processor.format_phase(ang - rtt_ph if self.__subtract_medium_phase else ang), rtt_ph

    def __process_reception(self, signal):
        signal.cut(self.__samples_to_cut)
        frequency, freq_sampling = signal.obtain_spectrum(self.__freq_points)
        f_min = self.__freq_cut*self.__freq_points//self.__receiver.sampling_rate
        d_f = (f_min+np.argmax(abs(frequency[int(f_min):])))*freq_sampling/self.__freq_points

        calculated_distance = (signal.period * d_f / signal.bandwidth - self.__componens_delay) * common.C/2

        distance = self.__distance_from_gui if self.__use_distance_from_gui else calculated_distance
        delta_r = common.C/2/signal.bandwidth * signal.length/self.__freq_points

        gain, target_phase, rtt_ph = self.__calculate_targets_properties(signal, frequency, distance)

        gain_to_tg = w2db(1/(np.power(4*np.pi, 2) * distance**4) if distance else float("inf"))

        if not self.__measurements[Measurement.Phase].n:
            if np.pi > target_phase > np.pi/2:
                self.__cut = 0

            elif -np.pi/2 > target_phase > -np.pi:
                self.__cut = 2 * np.pi

            else:
                self.__cut = np.pi

        calc_dist, tg_gain, tg_ph = self.__get_final_measurements(calculated_distance, gain, 
            np.rad2deg(signal_processor.format_phase(target_phase, self.__cut)))

        self.update_data.emit(round(d_f, 3), calc_dist, round(delta_r, 6), tg_gain, tg_ph, round(gain_to_tg, 8),
                              round(np.rad2deg(rtt_ph), 1), round(distance, 4))

        if signal.length > self.signal_length:
            data = signal.signal[:self.signal_length]
        else:
            data = np.concatenate((signal.signal, [0]*(self.signal_length-signal.length)))

        return data, abs(frequency[:self.__quantity_freq_samples]), np.rad2deg(target_phase)

    def __get_final_measurements(self, distance, gain, phase):
        """calculate the mean and 3 sigma of the measured distance, gain and phase."""
        self.__measurements[Measurement.Distance].add_sample(distance)
        self.__measurements[Measurement.Gain].add_sample(gain)
        self.__measurements[Measurement.Phase].add_sample(phase)

        return self.__measurements[Measurement.Distance].get_mean_std(n=3, decimals=3), \
               self.__measurements[Measurement.Gain].get_mean_std(n=3, decimals=4), \
               self.__measurements[Measurement.Phase].get_mean_std(n=3, decimals=1)

    def run(self, t=0):
        signal = self.__receiver.get_audio_data(self.__num_samples)

        if self.__measure_clutter:
            self.__measure_clutter = False

            if self.__use_external_clutter:
                self.__clutter.signal = self.__ext_clutter.signal*signal.applied_volume
            else:
                self.__clutter.signal = signal.signal

            self.__clutter.applied_volume = signal.applied_volume
            self.__clutter.frequency_sampling = signal.frequency_sampling

        signal.subtract_signals(self.__clutter)

        yield self.__process_reception(signal)

    def remove_clutter(self):
        self.__measure_clutter = True

    def restore_clutter(self):
        self.__clutter.signal = np.zeros(self.__clutter.length)

    def set_distance_from_gui(self, distance):
        self.__use_distance_from_gui = True
        self.__distance_from_gui = distance
        self.reset_statistics()

    def remove_distance(self):
        if self.__use_distance_from_gui:
            self.reset_statistics()

        self.__use_distance_from_gui = False

    def reset_statistics(self):
        self.__n = 0
        self.__measurements = {me: gc.GaussianCalculator() for me in Measurement}

    def rewind_audio(self):
        self.reset_statistics()
        self.__receiver.rewind()

    def set_auto_rewind(self, auto):
        self.__receiver.auto_rewind = auto

    def set_volume(self, volume):
        self.__receiver.volume = db2v(volume)

    def reset_volume(self):
        self.__receiver.reset_volume()

    def increase_volume(self):
        increment = 1
        self.__receiver.modify_volume(db2v(increment))
        return increment

    def decrease_volume(self):
        decrement = 1
        self.__receiver.modify_volume(db2v(-decrement))
        return decrement

    def use_external_signal(self, file_path):
        self.__receiver.track = file_path
        self.reset_statistics()
        self.__initialize_singal_properties()

    def use_external_clutter(self, file_path):
        receiver = f_receiver.FileReceiver(file_path)
        self.reset_statistics()
        self.__ext_clutter = receiver.get_audio_data(self.__num_samples)
        self.__use_external_clutter = True
        receiver.stop()

    def stop_using_external_clutter(self):
        self.__use_external_clutter = False

    def set_real_time_mode(self, real_time=True):
        if self.__receiver is not None:
            self.__receiver.stop()

        self.__receiver = r_receiver.RealReceiver() if real_time else f_receiver.FileReceiver()
        self.reset_statistics()

        if real_time:
            self.__initialize_singal_properties()
