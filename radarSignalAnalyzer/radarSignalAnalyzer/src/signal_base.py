import numpy as np
import scipy as sp
from scipy import signal as sn

import radarSignalAnalyzer.src.common as common


class Signal:

    def __init__(self, data, f0=common.F0, bw=common.BW, fs=common.Sampling_rate, applied_volume=1):
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
        """Obtain the signal."""
        return self.__signal

    @property
    def wavelength(self):
        """Obtain the signal's wavelength."""
        return self.__wavelength

    @property
    def frequency_sampling(self):
        """Obtain the signal's frequency sampling."""
        return self.__freq_sampling

    @property
    def central_freq(self):
        """Obtain the signal's central frequency."""
        return self.__f0

    @property
    def applied_volume(self):
        """Obtain the volume in which the signal is increased."""
        return self.__applied_volume

    @property
    def bandwidth(self):
        """Obtain the signal's bandwidth."""
        return self.__bandwidth

    @property
    def power(self):
        """Obtain the real received signal's power without the applied volume."""
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
        """Returs the period of the signal, in other words the pulse repetition time (PRT)."""
        return 1/self.__freq_sampling * self.__initial_length

    def subtract_signals(self, sign):
        """Subtract the signal with the received by parameter."""
        length = sign.length if self.__length > sign.length else self.__length
        self.signal = self.__signal[:length] - sign.signal[:length] * (self.__applied_volume/sign.applied_volume)

    def __get_initial_pos(self):
        initial_pos = 5
        if self.__initial_amplitude is None:
            self.__initial_amplitude = self.__signal[initial_pos]
            return initial_pos
        print(abs(self.__signal[initial_pos - 2: initial_pos + 2] - self.__initial_amplitude))
        return initial_pos

    def __make_periodical(self):
        """
        This method cuts the input signal in order to transform it in periodical.
        :returns: initial_pos: This is the index of the first value in the initial vector of data

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
        """
        Obtain the double of the signal's positive spectrum.

        :param amount_points: defines the FFT's length.
        :returns: a list with the signal's spectrum and the frequency sampling.
        """
        return sp.fft(self.__signal, amount_points)[:amount_points//2]*2/self.__length, self.__freq_sampling

    def obtain_spectrum2(self, amount_points, cut_length):
        """
        Obtain the double of the signal's positive spectrum rolling the signal.

        :param amount_points: defines the FFT's length.
        :returns: a list with the signal's spectrum and the frequency sampling.
        """
        return sp.fft(np.roll(self.__signal, (cut_length + self.__length)//2), amount_points)[:amount_points/2]*2/self.__length, self.__freq_sampling

    def standarize(self):
        """this function standarize the singal in order to put the central phase at the beginning."""
        '''
        previous_half_length = self.__length//2
        initial_pos = 0#self.__make_periodical()
        half_length = previous_half_length - initial_pos

        self.__signal = np.roll(self.__signal, -int(half_length))

        '''
        signal = self.__signal
        previous_half_length = self.__length//2
        # print(self.__length, len(self.__signal))
        initial_pos = 0
        # initial_pos = self.__make_periodical()
        # print(self.__length, len(self.__signal))
        # initial_pos = self.__make_periodical2()
        self.__signal = np.roll(self.__signal, int(-self.__length//2 + initial_pos))
        # self.__signal = np.roll(self.__signal, int(-previous_half_length + initial_pos))

    def cut(self, n_samples):
        """
        Discards the initial n_samples of the signal.

        :param n_samples: The amount of samples to discard.
        :raises Exception: When n_samples is not integer.
        """
        if not isinstance(n_samples, int) or isinstance(n_samples, bool):
            raise Exception('The amount of samples to cut the signal is not integer. Received {}'.format(n_samples))

        self.signal = self.__signal[n_samples:]
