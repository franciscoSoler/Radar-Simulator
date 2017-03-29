import matplotlib.animation as animation
from matplotlib.figure import Figure

from PyQt5 import QtCore
import numpy as np
import scipy as sp
import real_receiver as r_receiver
import file_receiver as f_receiver
import signal_processor
import distance_calculator as calculator
import common
import signal_base as sign


def get_mean_std(sample, mean, std, num_sample):
        """
        This method shows the mean and std value from the targets phase.
        It's assumed a gaussian distribution, so the shown value is mean +- 3std
        """

        n = num_sample - 1
        new_mean = (n * mean + sample) / num_sample

        if n == 0:
            return new_mean, 0

        new_std = np.sqrt(((n - 1) * std**2 + (sample - new_mean)**2) / n)

        return new_mean, new_std


class Controller(QtCore.QObject):

    update_data = QtCore.pyqtSignal(float, tuple, float, float, tuple, float, float, float)

    def __init__(self, max_freq, real_time=True):
        super(Controller, self).__init__()
        self.__measure_clutter = False
        self.__calculator = calculator.DistanceCalculator()

        self.__receiver = r_receiver.RealReceiver() if real_time else f_receiver.FileReceiver()
        self.__num_samples = self.__receiver.get_num_samples_per_period()

        while not self.__num_samples:
            self.__num_samples = self.__receiver.get_num_samples_per_period()
        self.__clutter = sign.Signal([0]*self.__num_samples)
        self.__freq_points = int(np.exp2(np.ceil(np.log2(self.__num_samples))+7))
        self.__quantity_freq_samples = max_freq*self.__freq_points//self.__receiver.sampling_rate
        self.__samples_to_cut = 0  # this variable cuts the beginning of the signal in order to delete some higher frequencies,
                                    # 30m = 0.008 samples --> no necesito cortar nada de nada
        self.__subtract_medium_phase = True
        self.__distance_from_gui = 0
        self.__use_distance_from_gui = 0

        self.__n = 0
        self.__mean_phase = 0
        self.__std_phase = 0
        self.__mean_dist = 0
        self.__std_dist = 0

    @property
    def signal_length(self):
        # TODO I have to delete this property, it's not a property
        return self.__num_samples - self.__samples_to_cut

    @property
    def freq_length(self):
        return self.__quantity_freq_samples

    def get_signal_range(self):
        d_t = 1/self.__receiver.sampling_rate
        return np.arange(0, d_t*self.signal_length, d_t)

    def get_frequency_range(self):
        d_f = self.__receiver.sampling_rate/self.__freq_points
        return np.arange(0, d_f*self.__freq_points//2, d_f)[:self.__quantity_freq_samples]

    def get_disance_from_freq(self, freq):
        signal = self.__receiver.get_audio_data(self.__num_samples)
        return signal.period * freq*common.C/(2*signal.bandwidth)

    def __process_reception(self, signal):
        self.__n += 1
        signal.cut(self.__samples_to_cut)
        freq_cut = 200
        frequency, freq_sampling = signal.obtain_spectrum(self.__freq_points)
        f_min = freq_cut*self.__freq_points//self.__receiver.sampling_rate
        d_f = (f_min+np.argmax(abs(frequency[f_min:])))*freq_sampling/self.__freq_points

        calculated_distance = signal.period * d_f*common.C/(2*signal.bandwidth)

        distance = self.__distance_from_gui if self.__use_distance_from_gui else calculated_distance
        delta_r = common.C/2/signal.bandwidth * signal.length/self.__freq_points
        # d_t = d_f*signal.period/signal.bandwidth
        # k = np.pi*signal.bandwidth/signal.period
        # phase = signal_processor.format_phase(2*np.pi*signal.central_freq * d_t - k*d_t**2)


        # This part is for calculating the distances phase shift
        k = 2*np.pi*signal.bandwidth/signal.period
        tau = 2*distance / common.C
        wc = 2*np.pi*signal.central_freq
        rtt_phase = signal_processor.format_phase(wc*tau - k*tau*signal.period/2 - k*tau**2/2)

        if np.argmax(abs(frequency)) > self.__quantity_freq_samples:
            raise Exception("el módulo máximo de la frecuencia dio en valires de frecuencia negativa en vez de \
                positiva. índice: {}".format(np.argmax(abs(frequency))))
            # If this exception is raised, please change the following lines with:
            # np.argmax(abs(frequency[:self.__quantity_freq_samples]))

        if self.__subtract_medium_phase:
            target_phase = signal_processor.format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - rtt_phase)
        else:
            # final_ph = signal_processor.format_phase(np.angle(frequency)[np.argmax(abs(frequency))])

            freqq = signal.obtain_spectrum2(self.__freq_points, self.__samples_to_cut)[0]
            target_phase = signal_processor.format_phase(np.angle(freqq)[np.argmax(abs(freqq))])

        gain_to_tg = 1/np.power(4*np.pi*distance, 4) if distance else float("inf")
        gain = signal.amplitude - gain_to_tg

        self.update_data.emit(round(d_f, 3), self.__get_final_dist(calculated_distance), round(delta_r, 6),
                              round(gain, 3), self.__get_final_phase(np.rad2deg(target_phase)),
                              round(gain_to_tg, 8), round(np.rad2deg(rtt_phase), 1), round(distance, 4))

        if signal.length > self.signal_length:
            data = signal.signal[:self.signal_length]
        else:
            data = np.concatenate((signal.signal, [0]*(self.signal_length-signal.length)))

        return data, abs(frequency[:self.__quantity_freq_samples]), np.rad2deg(target_phase)

    def __get_final_dist(self, distance):
        self.__mean_dist, self.__std_dist = get_mean_std(distance, self.__mean_dist, self.__std_dist, self.__n)
        return round(self.__mean_dist, 3), round(3*self.__std_dist, 3)

    def __get_final_phase(self, phase):
        """
        This method shows the mean and std value from the targets phase.
        It's assumed a gaussian distribution, so the shown value is mean +- 3std
        """
        self.__mean_phase, self.__std_phase = get_mean_std(phase, self.__mean_phase, self.__std_phase, self.__n)
        return round(self.__mean_phase, 1), round(3*self.__std_phase, 1)

    def run(self, t=0):
        while True:
            signal = self.__receiver.get_audio_data(self.__num_samples)

            if self.__measure_clutter:
                self.__measure_clutter = False
                self.__clutter.signal = signal.signal

            signal.subtract_signals(self.__clutter)

            yield self.__process_reception(signal)

    def remove_clutter(self):
        self.__measure_clutter = True

    def restore_clutter(self):
        self.__clutter.signal = np.zeros(self.__clutter.length)

    def set_distance_from_gui(self, distance):
        self.__use_distance_from_gui = True
        self.__distance_from_gui = distance

    def remove_distance(self):
        self.__use_distance_from_gui = False
