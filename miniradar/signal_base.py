import numpy as np
import scipy as sp
import common
import matplotlib.pyplot as plt


class Signal:

    def __init__(self, data, f0=2450E6, bw=330E6, fs=40000.):
        self.__signal = data
        self.__wavelength = common.C/f0
        self.__freq_sampling = fs
        self.__length = len(data)
        self.__bandwidth = bw

        self.__amplitude = 2/self.__length * np.max(np.abs(sp.fft(data)))

    @property
    def signal(self):
        return self.__signal

    @property
    def wavelength(self):
        return self.__wavelength

    @property
    def central_freq(self):
        return common.C/self.__wavelength

    @property
    def bandwidth(self):
        return self.__bandwidth

    @property
    def amplitude(self):
        return self.__amplitude

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

    @property
    def period(self):
        return 1/self.__freq_sampling * self.__length

    def subtract_signals(self, sign):
        if self.__length > sign.length:
            self.signal = self.__signal[:sign.length] - sign.signal
        else:
            self.__signal = self.__signal - sign.signal[:self.__length]

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
        initial_slope = self.__signal[delta + initial_pos] - self.__signal[initial_pos] > 0
        final_slope = self.__signal[last_pos] - self.__signal[last_pos - delta] > 0

        initial_sign = self.__signal[initial_pos] > 0
        final_sign = self.__signal[last_pos] > 0

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
        print(initial_pos, last_pos, len(self.__signal))
        self.signal = self.__signal[initial_pos:last_pos]
        return initial_pos

    def obtain_spectrum(self, amount_points):
        return sp.fft(self.__signal, amount_points)[:amount_points/2]*2/self.__length, self.__freq_sampling

    def standarize(self):
        """
        this function standarize the singal in order to put the central phase at the beginning
        """
        """
        previous_half_length = self.__length//2
        initial_pos = self.__make_periodical()
        half_length = previous_half_length - initial_pos

        self.__signal = np.roll(self.__signal, -half_length)
        """
        signal = self.__signal
        initial_pos = self.__make_periodical()
        self.__signal = np.roll(self.__signal, int(-self.__length//2 + initial_pos))
