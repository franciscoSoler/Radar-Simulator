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
        #todo cambiar
        self.__num_samples = 100
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
        phase = signal_processor.SignalProcessor.format_phase(2*np.pi*common.SignalProperties.F0 * d_t - k*d_t**2)

        final_ph = signal_processor.SignalProcessor.format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - phase)

        gain_to_tg = 1/np.power(4*np.pi*distance, 4)
        gain = signal.amplitude - gain_to_tg
        self.update_data(d_f, distance, delta_r, gain, final_ph, gain_to_tg, phase)
        return frequency

    def run(self, t=0):
        signal = self.__receiver.get_audio_data(self.__num_samples)
        
        if self.__measure_clutter:
            self.__measure_clutter = False
            self.__clutter = signal
        
        self.__remove_clutter(signal)

        return self.__process_reception(signal)
        """
        self.__calculator.calculate_fft_distance(signal, length)
        self.__calculator.calculate_zcc_distance2(signal[:length])

        self.__freq_points = int(np.exp2(np.ceil(np.log2(length))+4))
        final_spectrum = sp.fft(np.roll(signal, -initial_length//2), self.__freq_points)[:self.__freq_points/2]*2./length

        self.frequency = abs(final_spectrum).argmax() * float(SAMPLING_RATE)/self.__freq_points

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
        """

    def remove_clutter(self):
        self.__measure_clutter = True

    def restore_clutter(self):
        self.__clutter.signal = np.zeros(self.__clutter.length)
