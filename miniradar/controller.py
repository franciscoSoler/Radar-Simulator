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


class Controller(QtCore.QObject):

    update_data = QtCore.pyqtSignal(float, float, float, float, float, float, float)

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
        self.__samples_to_cut = 150 # this variable cuts the beginning of the signal in order to delete some higher frequencies,
                                # I need to calculate properly which will be this value.
        self.__subtract_medium_phase = False

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
        # signal.standarize()
        signal.cut(self.__samples_to_cut)
        freq_cut = 200
        frequency, freq_sampling = signal.obtain_spectrum(self.__freq_points)
        f_min = freq_cut*self.__freq_points//self.__receiver.sampling_rate
        d_f = (f_min+np.argmax(abs(frequency[f_min:])))*freq_sampling/self.__freq_points

        distance = signal.period * d_f*common.C/(2*signal.bandwidth)
        delta_r = common.C/2/signal.bandwidth * signal.length/self.__freq_points
        d_t = d_f*signal.period/signal.bandwidth

        k = np.pi*signal.bandwidth/signal.period
        phase = signal_processor.format_phase(2*np.pi*signal.central_freq * d_t - k*d_t**2)

        if np.argmax(abs(frequency)) > self.__quantity_freq_samples:
            raise Exception("el módulo máximo de la frecuencia dio en valires de frecuencia negativa en vez de \
                positiva. índice: {}".format(np.argmax(abs(frequency))))
            # If this exception is raised, please change the following lines with:
            # np.argmax(abs(frequency[:self.__quantity_freq_samples]))

        if self.__subtract_medium_phase:
            final_ph = signal_processor.format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - phase)
        else:
            final_ph = signal_processor.format_phase(np.angle(frequency)[np.argmax(abs(frequency))])

        gain_to_tg = 1/np.power(4*np.pi*distance, 4) if distance else float("inf")
        gain = signal.amplitude - gain_to_tg
        self.update_data.emit(round(d_f, 3), round(distance, 3), round(delta_r, 6), round(gain, 3),
                              round(signal_processor.rad2deg(final_ph)), round(gain_to_tg, 8),
                              round(signal_processor.rad2deg(phase)))

        if signal.length > self.signal_length:
            data = signal.signal[:self.signal_length]
        else:
            data = np.concatenate((signal.signal, [0]*(self.signal_length-signal.length)))

        return data, abs(frequency[:self.__quantity_freq_samples]), signal_processor.rad2deg(final_ph)

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
