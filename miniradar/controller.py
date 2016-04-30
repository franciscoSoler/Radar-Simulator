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

    def __init__(self, quantity_samples, real_time=True):
        super(Controller, self).__init__()
        self.__measure_clutter = False
        self.__calculator = calculator.DistanceCalculator()

        self.__receiver = r_receiver.RealReceiver() if real_time else f_receiver.FileReceiver()
        self.__num_samples = self.__receiver.get_num_samples_per_period()

        while not self.__num_samples:
            self.__num_samples = self.__receiver.get_num_samples_per_period()

        self.__clutter = sign.Signal([0]*self.__num_samples)
        self.__freq_points = int(np.exp2(np.ceil(np.log2(self.__num_samples))+7))
        self.__quantity_freq_samples = quantity_samples

    @property
    def freq_length(self):
        return self.__freq_points//2

    def get_frequency_range(self):
        signal = self.__receiver.get_audio_data(self.__num_samples)
        d_f = signal.frequency_sampling/self.__freq_points
        return np.arange(0, d_f*self.__freq_points//2, d_f)[:self.__quantity_freq_samples]

    def get_disance_from_freq(self, freq):
        signal = self.__receiver.get_audio_data(self.__num_samples)
        return signal.period * freq*common.C/(2*signal.bandwidth)

    def __process_reception(self, signal):
        signal.standarize()
        frequency, freq_sampling = signal.obtain_spectrum(self.__freq_points)

        d_f = np.argmax(abs(frequency))*freq_sampling/self.__freq_points

        distance = signal.period * d_f*common.C/(2*signal.bandwidth)
        delta_r = common.C/2/signal.bandwidth * signal.length/self.__freq_points
        d_t = d_f*signal.period/signal.bandwidth

        k = np.pi*signal.bandwidth/signal.period
        phase = signal_processor.format_phase(2*np.pi*signal.central_freq * d_t - k*d_t**2)

        final_ph = signal_processor.format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - phase)

        gain_to_tg = 1/np.power(4*np.pi*distance, 4) if distance else float("inf")
        gain = signal.amplitude - gain_to_tg
        self.update_data.emit(d_f, distance, delta_r, gain, final_ph, gain_to_tg, phase)
        return abs(frequency[:self.__quantity_freq_samples]), freq_sampling/self.__freq_points

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
