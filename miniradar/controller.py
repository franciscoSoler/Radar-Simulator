import matplotlib.animation as animation
from matplotlib.figure import Figure

from PyQt5 import QtCore
import numpy as np
import scipy as sp
import signal_receiver as receiver
import signal_processor
import distance_calculator as calculator
import common


class Controller(QtCore.QObject):

    update_data = QtCore.pyqtSignal(float, float, float, float, float, float, float)

    def __init__(self):
        super(Controller, self).__init__()
        self.__measure_clutter = True
        self.__clutter = None
        self.__calculator = calculator.DistanceCalculator()

        self.__receiver = receiver.SignalReceiver()
        self.__num_samples = self.__receiver.get_num_samples_per_period()
        #TODO cambiar
        # self.__num_samples = 500
        while not self.__num_samples:
            self.__num_samples = self.__receiver.get_num_samples_per_period()

        self.__freq_points = int(np.exp2(np.ceil(np.log2(self.__num_samples))+4))

    def __remove_clutter(self, signal):
        signal.subtract_signals(self.__clutter)


    def __process_reception(self, signal):
        signal.standarize()
        frequency, freq_sampling = signal.obtain_spectrum(self.__freq_points)

        d_f = np.argmax(abs(frequency))*freq_sampling/self.__freq_points
        distance = common.SignalProperties.T * d_f*common.SignalProperties.C/(2*common.SignalProperties.B)
        delta_r = common.SignalProperties.C/2/common.SignalProperties.B * signal.length/self.__freq_points
        d_t = d_f*common.SignalProperties.T/common.SignalProperties.B

        k = np.pi*common.SignalProperties.B/common.SignalProperties.T
        phase = signal_processor.format_phase(2*np.pi*common.SignalProperties.F0 * d_t - k*d_t**2)

        final_ph = signal_processor.format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - phase)

        gain_to_tg = 1/np.power(4*np.pi*distance, 4) if distance else float("inf")
        gain = signal.amplitude - gain_to_tg
        self.update_data.emit(d_f, distance, delta_r, gain, final_ph, gain_to_tg, phase)
        return abs(frequency), freq_sampling/self.__freq_points

    def run(self, t=0):
        while True:
            signal = self.__receiver.get_audio_data(self.__num_samples)

            if self.__measure_clutter:
                self.__measure_clutter = False
                self.__clutter = signal

            self.__remove_clutter(signal)

            yield self.__process_reception(signal)

    def remove_clutter(self):
        self.__measure_clutter = True

    def restore_clutter(self):
        self.__clutter.signal = np.zeros(self.__clutter.length)
