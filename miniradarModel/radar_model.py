#!/usr/bin/python3.4
__author__ = 'francisco'

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt


def format_phase(phase):
    return (phase + np.pi) % (2*np.pi) - np.pi


class SignalProperties:
    F0 = 2.450E6
    C = 299792458
    B = 0.300e6
    # B = 0.000001
    T = 0.5
    Freq_sampling = 5.6E6
    Time = 0.5


class SignalGenerator:

    def __init__(self):
        self.__real_b = 330.E6

    def recalculate_initial_time(self, initial_time, bandwidth, period):
        d_f = self.__real_b*initial_time/period
        print("real beat frequency", d_f)
        return d_f*period/bandwidth

    def generate_chirp(self, amplitude, time, phi_0, initial_time=0., freq_sampling=SignalProperties.Freq_sampling,
                       period=SignalProperties.T, f0=SignalProperties.F0, bandwidth=SignalProperties.B):
        d_t = self.recalculate_initial_time(initial_time, bandwidth, period)
        print("real round trip time", d_t)
        t = np.arange(0, time, 1./freq_sampling) % period - d_t
        # plt.plot(t)
        return Signal(amplitude, t, f0, bandwidth, period, phi_0, freq_sampling)

    @property
    def real_b(self):
        return self.__real_b


class Signal:

    def __init__(self, amplitude, t, f0=2.450E6, bw=0.3E6, period=0.1, phi_0=0, fs=1000.):
        k = 2*np.pi*bw/period
        wc = 2*np.pi*f0
        self.__signal = amplitude*np.sin(wc*t + k/2*np.power(t, 2) - k*period/2*t + phi_0)
        self.__wavelength = SignalProperties.C/f0
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

    @signal.setter
    def signal(self, sign):
        self.__signal = sign

    @length.setter
    def length(self, length):
        self.__length = length

    @freq_sampling.setter
    def freq_sampling(self, frequency):
        self.__freq_sampling = frequency

    @amplitude.setter
    def amplitude(self, amp):
        self.__amplitude = amp


class Radar:

    def __init__(self, amp=1., phi=0., max_freq_lpf=10e3, adc_freq=40E3):
        self.__amplitude = amp
        self.__initial_phase = phi
        self.__time = SignalProperties.Time
        self.__adc_freq = adc_freq
        self.__tx_signal = None

        self.__signal_gen = SignalGenerator()
        self.__lpf = LowPassFilter(max_freq_lpf, adc_freq)

    def transmit(self):
        self.__tx_signal = self.__signal_gen.generate_chirp(self.__amplitude, self.__time, self.__initial_phase)
        return self.__tx_signal

    def receive(self, rx_signal):
        signal_mixed = Mixer.mix_signals(self.__tx_signal, rx_signal)
        return self.__lpf.filter_signal(signal_mixed)

    @staticmethod
    def __calculate_gain(k, sw):
        m = 3
        val_range = np.arange(-m, m+1)
        spectrum = abs(np.array([sw[k+i] - (sw[k+i-1] + sw[k+i+1])/2 for i in val_range]))
        power_spec = np.power(spectrum, 2)/len(sw)
        offset = np.dot(val_range, power_spec)/np.sum(power_spec)
        calc1 = power_spec[m+1] / (power_spec[m] + power_spec[m+1])
        calc2 = -power_spec[m-1] / (power_spec[m] + power_spec[m-1])
        offset2 = calc1 if calc1 < abs(calc2) else calc2
        print("offsets", offset, offset2, calc1, calc2)
        return offset/2 if abs(offset) < 0.05 else offset2

    def process_reception(self, signal):
        pad = 1
        new_signal = signal.signal[::pad]  # /pad
        # signal_padded = np.zeros(pad*signal.length)
        signal_padded = np.zeros(pad*len(new_signal))
        """
        signal_padded = np.zeros(1 + pad*(signal.length-1))
        signal_padded[::pad] = signal.signal
        frequency = sp.fft(np.roll(signal_padded, -int(len(signal_padded)/2)))[:len(signal_padded)/2]/len(signal_padded)
        """
        # signal_padded[::pad] = np.roll(signal.signal, -int(signal.length/2))
        signal_padded[:signal.length] = np.roll(signal.signal, -int(signal.length/2))  # * np.hamming(signal.length)
        # frequency = sp.fft(signal_padded, int(np.exp2(np.ceil(np.log2(len(signal_padded))))))[:len(signal_padded)/2]/len(signal_padded)
        # frequency = sp.fft(signal.signal, int(np.exp2(np.ceil(np.log2(signal.length))+5)))[:np.exp2(np.ceil(np.log2(signal.length))+5)/2]
        frequency = sp.fft(signal.signal, int(np.exp2(np.ceil(np.log2(signal.length))+5)))[:np.exp2(np.ceil(np.log2(signal.length))+5)/2]
        # frequency = sp.fft(signal_padded*np.blackman(len(signal_padded)))[:len(signal_padded)/2]/len(signal_padded)
        # frequency = sp.fft(signal_padded*np.hanning(len(signal_padded)))[:len(signal_padded)/2]/len(signal_padded)
        # frequency = sp.fft(signal_padded*np.hamming(len(signal_padded)))[:len(signal_padded)/2]/len(signal_padded)

        # n_max = signal.length/2/pad
        # frequency[n_max:] = 1e-12
        # frequency *= pad
        print("length", signal.length, len(signal_padded))
        # d_f = np.argmax(abs(frequency))*self.__adc_freq/signal.length/pad
        d_f = np.argmax(abs(frequency))*self.__adc_freq/int(np.exp2(np.ceil(np.log2(signal.length))+5))
        # d_f = np.argmax(abs(frequency))*self.__adc_freq/int(np.exp2(np.ceil(np.log2(len(signal_padded)))))
        d_f1 = np.argmax(abs(frequency))*self.__adc_freq/len(signal_padded)
        # d_f1 = np.argmax(abs(frequency))/SignalProperties.Time
        # d_f = np.argmax(abs(frequency))*self.__adc_freq/len(signal_padded)
        distance = SignalProperties.T * d_f*SignalProperties.C/(2*self.__signal_gen.real_b)
        print("frequency to target:", d_f, "pos:", np.argmax(abs(frequency)))
        delta_r = SignalProperties.C/2/self.__signal_gen.real_b/pad
        print("distance to target:", distance, delta_r)

        d_t = np.argmax(abs(frequency))/SignalProperties.B
        # d_t = np.argmax(abs(frequency))/SignalProperties.B/pad
        d_t1 = d_f1*SignalProperties.T/SignalProperties.B
        print("round trip time", d_t, d_t1)

        k = np.pi*SignalProperties.B/SignalProperties.T
        phase = format_phase(2*np.pi*SignalProperties.F0 * d_t - k*d_t**2)
        # phase = format_phase(2*np.pi*SignalProperties.F0 * d_t1 - k*d_t1**2)

        final_ph = format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - phase)
        print("measured phase:", format_phase(np.angle(frequency)[np.argmax(abs(frequency))]), "distance phase:", phase)
        print("target's phase", final_ph)

        delta_f = self.__calculate_gain(np.argmax(abs(frequency)), frequency)
        d_f = (np.argmax(abs(frequency)) + delta_f)*self.__adc_freq/signal.length
        distance = SignalProperties.T * d_f*SignalProperties.C/(2*self.__signal_gen.real_b)
        print("frequency to target:", d_f)
        print("distance to target:", distance)

        n = np.arange(len(frequency))
        b = SignalProperties.B
        fre = frequency * np.exp(-1j*(2*np.pi*SignalProperties.F0 * n/b - k*np.power(n/b, 2)))
        """
        ang = np.angle(sp.ifft(fre)[0])
        ang1 = np.angle(sp.ifft(fre[:len(fre)/2])[0])
        """
        ang = np.angle(sp.ifft(sp.fft(signal_padded, int(np.exp2(np.ceil(np.log2(len(signal_padded)))))))[0])
        ang1 = np.angle(sp.ifft(sp.fft(signal_padded, int(np.exp2(np.ceil(np.log2(len(signal_padded))))))[:len(signal_padded)/2])[0])
        print("angles in time", ang, ang1, "angle in freq", np.angle(fre[np.argmax(abs(fre))]))

        wavelength = SignalProperties.C/SignalProperties.F0
        r_f1 = wavelength * ang / (4*np.pi)
        r_f2 = wavelength * ang1 / (4*np.pi)
        print("r_fines", r_f1, r_f2)
        plt.figure()
        plt.subplot(211)
        plt.plot(np.abs(frequency))
        plt.subplot(212)
        # plt.plot(signal.signal[:10000])
        plt.plot(np.abs(sp.fft(signal.signal, int(np.exp2(np.ceil(np.log2(signal.length))))))[:signal.length/2])
        # plt.plot(np.arange(0, len(signal_padded)/2)/SignalProperties.Time/pad, 20*np.log10(abs(frequency)))
        plt.show()


class Mixer:

    def __init__(self):
        pass

    @staticmethod
    def mix_signals(signal1, signal2):
        """
        :param signal1: array representing the first signal to mix
        :param signal2: array representing the second signal to mix
        :return: the mixed signal
        """
        signal = Signal(1/2*signal1.amplitude*signal2.amplitude, np.array([1, 2]), fs=signal1.freq_sampling)
        signal.signal = signal1.signal * signal2.signal
        signal.length = signal1.length
        return signal


class LowPassFilter:

    def __init__(self, max_freq, adc_freq):
        self.__upper_freq = max_freq
        self.__adc_freq = adc_freq

    def filter_signal(self, signal):
        """
        :param signal: the input signal to filter
        :return:
        """
        amount_points = int(np.exp2(np.ceil(np.log2(signal.length))))
        freq = sp.fft(signal.signal, amount_points)

        n_max = self.__upper_freq*signal.length/signal.freq_sampling
        freq[n_max:-n_max] = 0

        samples = self.__adc_freq*len(freq)/signal.freq_sampling/2 + 1

        output_signal = np.real(sp.ifft(np.concatenate((freq[:samples], freq[-samples:])))
                                )*self.__adc_freq/signal.freq_sampling

        output = Signal(signal.amplitude, np.array([1, 2]), fs=signal.freq_sampling)
        output.signal = output_signal[:signal.length*self.__adc_freq/signal.freq_sampling]
        output.length = int(signal.length*self.__adc_freq/signal.freq_sampling)
        return output


class Medium:

    def __init__(self, obj):
        """
        :param obj: the illuminated object
        :return:
        """
        self.__real_f0 = 2450E6
        self.__object = obj
        self.__attenuation = lambda x: 1/np.power(4*np.pi*x, 4)

    def propagate_signal(self, signal, dist_to_obj=5.):
        d_t = 2.*dist_to_obj/SignalProperties.C
        sign_gen = SignalGenerator()

        rx_ph = format_phase(self.__object.phase + signal.phi_0)
        gain = self.__object.gain * np.power(signal.wavelength, 2) * self.__attenuation(dist_to_obj)

        return sign_gen.generate_chirp(gain * signal.amplitude, SignalProperties.Time, rx_ph, d_t)


class Object:

    def __init__(self, gain=1., phase=0.):
        self.__gain = gain
        self.__phase = phase

    @property
    def gain(self):
        return self.__gain

    @property
    def phase(self):
        return self.__phase


if __name__ == "__main__":
    radar = Radar()

    tx_signal = radar.transmit()
    ideal_dist = 37.8953243398
    ideal_phase = 0*np.pi/2
    medium = Medium(Object(1, ideal_phase))
    print("ideal distance", ideal_dist)
    print("ideal phase", ideal_phase)
    rx_sign = medium.propagate_signal(tx_signal, dist_to_obj=ideal_dist)  # 38.1554037455
    # rx_sign = medium.propagate_signal(tx_signal, dist_to_obj=5.905002960606061)
    # rx_sign = medium.propagate_signal(tx_signal, dist_to_obj=6.3592339575757579)

    output = radar.receive(rx_sign)
    radar.process_reception(output)
    exit(0)
