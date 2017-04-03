import numpy as np
import common


class Signal:

    def __init__(self, amplitude, t, f0=common.SignalProperties.F0, bw=common.SignalProperties.B, 
                 period=common.SignalProperties.T, phi_0=0, fs=1000.):
        k = 2*np.pi*bw/period
        wc = 2*np.pi*f0
        self.__signal = amplitude*np.cos(wc*t + k/2*np.power(t, 2) - k*period/2*t + phi_0)
        self.__wavelength = common.SignalProperties.C/f0
        self.__amplitude = amplitude
        self.__phi_0 = phi_0
        self.__freq_sampling = fs
        self.__length = len(t)

    @property
    def signal(self):
        return self.__signal

    @property
    def wavelength(self):
        return self.__wavelength

    @property
    def amplitude(self):
        return self.__amplitude

    @property
    def phi_0(self):
        return self.__phi_0

    @property
    def freq_sampling(self):
        return self.__freq_sampling

    @property
    def length(self):
        return self.__length

    @property
    def power(self):
        return self.__signal.dot(self.__signal)/self.__length

    @signal.setter
    def signal(self, sign):
        self.__signal = sign
        self.__length = len(sign)
        self.__amplitude = np.sqrt(sign.dot(sign)/len(sign))

    @length.setter
    def length(self, length):
        self.__length = length

    @freq_sampling.setter
    def freq_sampling(self, frequency):
        self.__freq_sampling = frequency

    @amplitude.setter
    def amplitude(self, amp):
        self.__amplitude = amp
