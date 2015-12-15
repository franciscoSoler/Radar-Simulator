#!/usr/bin/python3.4
import common
import signal_base as sign
import signal_processor as signalProcessor
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

__author__ = 'francisco'


def format_phase(phase):
    return (phase + np.pi) % (2*np.pi) - np.pi


class SignalGenerator:

    def __init__(self):
        self.__real_b = 330.E6

    def recalculate_initial_time(self, initial_time, bandwidth, period):
        d_f = self.__real_b*initial_time/period
        print("real beat frequency", d_f)
        return d_f*period/bandwidth

    def generate_chirp(self, amplitude, time, phi_0, initial_time=0., freq_sampling=common.SignalProperties.Freq_sampling,
                       period=common.SignalProperties.T, f0=common.SignalProperties.F0, bandwidth=common.SignalProperties.B):
        d_t = self.recalculate_initial_time(initial_time, bandwidth, period)
        print("real round trip time", d_t)
        t = np.arange(0, time, 1./freq_sampling) % period - d_t
        sign.Signal(amplitude, t, f0, bandwidth, period, phi_0, freq_sampling)
        # plt.plot(t)
        return sign.Signal(amplitude, t, f0, bandwidth, period, phi_0, freq_sampling)

    @property
    def real_b(self):
        return self.__real_b


class Radar:

    def __init__(self, amp=1., phi=0., max_freq_lpf=10e3, adc_freq=40E3):
        self.__amplitude = amp
        self.__initial_phase = phi
        self.__time = common.SignalProperties.Time
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
        previous_half_length = int(signal.length/2)
        initial_pos, final_pos = signalProcessor.SignalProcessor.make_periodical(signal)
        half_length = previous_half_length - initial_pos

        amount_points = int(np.exp2(np.ceil(np.log2(signal.length))+5))
        frequency = sp.fft(np.roll(signal.signal, -half_length), amount_points)[:amount_points/2]*2/signal.length

        d_f = np.argmax(abs(frequency))*self.__adc_freq/amount_points
        print()
        print("Measured frequency to target:", d_f, "position:", np.argmax(abs(frequency)))

        distance = common.SignalProperties.T * d_f*common.SignalProperties.C/(2*self.__signal_gen.real_b)
        delta_r = common.SignalProperties.C/2/self.__signal_gen.real_b * signal.length/amount_points
        print("Measured distance to target:", distance, "Delta distance:", delta_r)

        d_t = d_f*common.SignalProperties.T/common.SignalProperties.B
        print("Measured round trip time:", d_t)

        k = np.pi*common.SignalProperties.B/common.SignalProperties.T
        phase = format_phase(2*np.pi*common.SignalProperties.F0 * d_t - k*d_t**2)

        final_ph = format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - phase)
        print("Measured target's phase:", final_ph)
        print()

        delta_f = self.__calculate_gain(np.argmax(abs(frequency)), frequency)
        d_f = (np.argmax(abs(frequency)) + delta_f)*self.__adc_freq/signal.length
        distance = common.SignalProperties.T * d_f*common.SignalProperties.C/(2*self.__signal_gen.real_b)
        print("Measured frequency to target:", d_f)
        print("Measured distance to target:", distance)

        plt.plot(np.abs(frequency))
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
        signal = sign.Signal(1/2*signal1.amplitude*signal2.amplitude, np.array([1, 2]), fs=signal1.freq_sampling)
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

        signal_filtered = sign.Signal(signal.amplitude, np.array([1, 2]), fs=self.__adc_freq)
        signal_filtered.signal = output_signal[:signal.length*self.__adc_freq/signal.freq_sampling]

        return signal_filtered


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
        d_t = 2.*dist_to_obj/common.SignalProperties.C
        sign_gen = SignalGenerator()

        rx_ph = format_phase(self.__object.phase + signal.phi_0)
        gain = self.__object.gain * np.power(signal.wavelength, 2) * self.__attenuation(dist_to_obj)

        return sign_gen.generate_chirp(gain * signal.amplitude, common.SignalProperties.Time, rx_ph, d_t)


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
    ideal_phase = 2*np.pi/2
    medium = Medium(Object(1, ideal_phase))
    print("ideal distance", ideal_dist)
    print("ideal phase", ideal_phase)
    rx_sign = medium.propagate_signal(tx_signal, dist_to_obj=ideal_dist)

    output = radar.receive(rx_sign)
    radar.process_reception(output)
    exit(0)
