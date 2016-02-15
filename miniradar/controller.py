import matplotlib.animation as animation
from matplotlib.figure import Figure

from PyQt5 import QtCore
import numpy as np
import scipy as sp
import signal_receiver as receiver
import distance_calculator as calculator
import common


CUT = 0


class Controller(QtCore.QObject):

    update = QtCore.pyqtSignal(np.ndarray)

    def __init__(self):
        super(Controller, self).__init__()
        self.__measure_clutter = True
        self.__clutter_time = None
        self.__clutter_data = None
        self.__clutter = None
        self.__calculator = calculator.DistanceCalculator()

        self.__receiver = receiver.SignalReceiver()
        self.__num_samples = self.__receiver.get_num_samples_per_period()
        #todo cambiar
        self.__num_samples = 100
        while not self.__num_samples:
            self.__num_samples = self.__receiver.get_num_samples_per_period()

    def run(self, t=0):
        time, initial_length, flanks = self.__receiver.get_audio_data(self.__num_samples - CUT)

        if self.__measure_clutter:
            self.__measure_clutter = False
            self.__clutter_time = time[:, 0]

        # self.__calculator.calculate_zcc_distance(audio_data, flanks)

        if len(time) > initial_length:
            length = initial_length
            signal = time[:initial_length, 0] - self.__clutter_time
        else:
            length = len(time)
            signal = time[:, 0] #- self.__clutter_time[:len(time)]

        self.__calculator.calculate_fft_distance(signal, length)
        self.__calculator.calculate_zcc_distance2(signal[:length])

        amount_points = int(np.exp2(np.ceil(np.log2(length))+4))
        final_spectrum = sp.fft(np.roll(signal, -int(initial_length/2)), amount_points)[:amount_points/2]*2./length

        self.frequency = abs(final_spectrum).argmax() * float(SAMPLING_RATE)/amount_points

        period = length/float(SAMPLING_RATE)

        self.distance = period * C * self.frequency / (2*B)

        self.d_t = self.frequency*period/B

        def format_phase(x):
            return (x + np.pi) % (2*np.pi) - np.pi

        k = np.pi*B/period
        rtt_phase = format_phase(2*np.pi*F0 * self.d_t - k*self.d_t**2)

        self.phase = format_phase(np.angle(final_spectrum)[np.argmax(abs(final_spectrum))] - rtt_phase)

        self.spectrum_data.set_data('amplitude', abs(final_spectrum))
        self.time_data.set_data('amplitude', signal)
        self.time_data1.set_data('amplitude', time[:, 1])
        spectrogram_data = self.spectrogram_plotdata.get_data('imagedata')
        spectrogram_data = hstack((spectrogram_data[:, 1:],
                                   transpose([abs(final_spectrum)])))
        print(final_spectrum.size)

        self.spectrogram_plotdata.set_data('imagedata', spectrogram_data)
        self.spectrum_plot.request_redraw()
        return final_spectrum

    def remove_clutter(self):
        self.__measure_clutter = True

    def restore_clutter(self):
        self.__clutter_time = np.zeros(len(self.__clutter_time))
