import numpy as np
import scipy as sp
from scipy import signal as sn
import common
import matplotlib.pyplot as plt


class Signal:

    def __init__(self, data, f0=2450E6, bw=330E6, fs=44100., applied_volume=1):
        self.__signal = np.array(data)
        self.__wavelength = common.C/f0
        self.__f0 = f0
        self.__freq_sampling = fs
        self.__applied_volume = applied_volume

        self.__initial_length = len(data)
        self.__length = self.__initial_length
        self.__bandwidth = bw
        self.__initial_amplitude = None

    @property
    def signal(self):
        return self.__signal

    @property
    def wavelength(self):
        return self.__wavelength

    @property
    def frequency_sampling(self):
        return self.__freq_sampling

    @property
    def central_freq(self):
        return self.__f0

    @property
    def applied_volume(self):
        return self.__applied_volume

    @property
    def bandwidth(self):
        return self.__bandwidth

    @property
    def power(self):
        """
        This method returns the real received signal's power without the applied volume
        """
        return self.__signal.dot(self.__signal)/self.__length/(self.__applied_volume**2)

    @property
    def length(self):
        return self.__length

    @signal.setter
    def signal(self, sign):
        self.__signal = sign
        self.__length = len(sign)

    @length.setter
    def length(self, length):
        self.__length = length

    @frequency_sampling.setter
    def frequency_sampling(self, fs):
        self.__freq_sampling = fs

    @applied_volume.setter
    def applied_volume(self, volume):
        self.__applied_volume = volume

    @property
    def period(self):
        # this period is the pulse repetition time (PRT)
        return 1/self.__freq_sampling * self.__initial_length

    def subtract_signals(self, sign):
        length = sign.length if self.__length > sign.length else self.__length
        self.signal = self.__signal[:length] - sign.signal[:length] * (self.__applied_volume/sign.applied_volume)

    # def __save_initial_amplitude(self, amplitude):
    #     if self.__initial_amplitude is None:
    #         self.__initial_amplitude = amplitude

    def __get_initial_pos(self):
        initial_pos = 5
        if self.__initial_amplitude is None:
            self.__initial_amplitude = self.__signal[initial_pos]
            return initial_pos
        print(abs(self.__signal[initial_pos - 2: initial_pos + 2] - self.__initial_amplitude))
        return initial_pos

    def __make_periodical(self):
        """
        this method cuts the input signal in order to transform it in periodical.
        :return initial_pos: This is the index of the first value in the initial vector of data

        """
        amount_points = int(np.exp2(np.ceil(np.log2(self.__length))))
        max_freq = np.argmax(abs(sp.fft(self.__signal, amount_points)[:amount_points/2]))
        period_length = amount_points / max_freq if max_freq else float("inf")

        if period_length > self.__length:
            return self.__length//2

        half_period = period_length//2

        initial_pos = half_period
        last_pos = -half_period
        delta = 5

        initial_pos = self.__get_initial_pos()
        last_pos = -delta

        initial_slope = self.__signal[delta + initial_pos] - self.__signal[initial_pos] > 0
        final_slope = self.__signal[last_pos] - self.__signal[last_pos - delta] > 0

        initial_sign = self.__signal[initial_pos] > 0
        final_sign = self.__signal[last_pos] > 0
        # this need more than one period in the datafile
        if initial_slope ^ final_slope:
            # in this case the slope of the initial/final signal is not the same
            last_pos -= half_period

        if initial_sign ^ final_sign:
            # in this case the sign of the initial/final signal is not the same
            last_pos -= int(3*period_length/4) if final_sign ^ final_slope else int(period_length/4)

        # now I have to move through the signal searching for the closest value to the initial point
        movement = 1 if initial_slope ^ (self.__signal[last_pos] > self.__signal[initial_pos]) else -1

        def calc_distance(x):
            return abs(x - self.__signal[initial_pos])
        while calc_distance(self.__signal[last_pos]) > calc_distance(self.__signal[last_pos + movement]):
            last_pos += movement

        # now I have to remove the last point if necessary
        last_pos -= 0 if initial_slope ^ (self.__signal[last_pos] > self.__signal[initial_pos]) else 1

        if initial_pos > self.__length + last_pos:
            return self.__length//2
        print(initial_pos, last_pos, len(self.__signal), movement, self.__signal[initial_pos], [self.__signal[last_pos-1], self.__signal[last_pos], self.__signal[last_pos+1]])
        self.signal = self.__signal[initial_pos:last_pos]
        return initial_pos

    def obtain_spectrum(self, amount_points):
        # this method returns the double of the spectrum and its frequency sampling
        # return sp.fft(np.blackman(self.__length) * self.__signal, amount_points)[:amount_points/2]*2/self.__length, self.__freq_sampling
        return sp.fft(self.__signal, amount_points)[:amount_points/2]*2/self.__length, self.__freq_sampling

    def obtain_spectrum2(self, amount_points, cut_length):
        # this method returns the double of the spectrum and its frequency sampling
        return sp.fft(np.roll(self.__signal, (cut_length + self.__length)//2), amount_points)[:amount_points/2]*2/self.__length, self.__freq_sampling

    def standarize(self):
        """
        this function standarize the singal in order to put the central phase at the beginning
        """
        """
        previous_half_length = self.__length//2
        initial_pos = 0#self.__make_periodical()
        half_length = previous_half_length - initial_pos

        self.__signal = np.roll(self.__signal, -int(half_length))

        """
        signal = self.__signal
        previous_half_length = self.__length//2
        # print(self.__length, len(self.__signal))
        initial_pos = 0
        # initial_pos = self.__make_periodical()
        # print(self.__length, len(self.__signal))
        # initial_pos = self.__make_periodical2()
        self.__signal = np.roll(self.__signal, int(-self.__length//2 + initial_pos))
        # self.__signal = np.roll(self.__signal, int(-previous_half_length + initial_pos))

    def cut(self, samples):
        self.signal = self.__signal[samples:]
