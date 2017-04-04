#!/usr/bin/python3
import common
import signal_base as sign
import signal_processor as signalProcessor
import numpy as np
import scipy as sp
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt

__author__ = 'francisco'


def format_phase(phase):
    return (phase + np.pi) % (2*np.pi) - np.pi


class SignalGenerator:

    def __init__(self):
        self.__real_b = 300.E6

    def recalculate_initial_time(self, initial_time, bandwidth, period):
        d_f = self.__real_b*initial_time/period
        # print("Real beat frequency:\t", d_f, '\t', bandwidth*initial_time/period)
        return d_f*period/bandwidth

    def generate_chirp(self, amplitude, time, phi_0, initial_time=0.,
                       freq_sampling=common.SignalProperties.Freq_sampling,
                       period=common.SignalProperties.T, f0=common.SignalProperties.F0,
                       bandwidth=common.SignalProperties.B):
        self.recalculate_initial_time(initial_time, bandwidth, period)
        # k = 2*np.pi*bandwidth/period
        # wc = 2*np.pi*f0
        # if initial_time:
        #     print('Real deramped phase:\t', format_phase(wc*initial_time - k*initial_time*period/2 - k*initial_time**2/2))

        t = np.arange(-initial_time, time - initial_time, 1./freq_sampling) % period
        # t = np.linspace(-initial_time, time - initial_time, freq_sampling*time, endpoint=False) % period

        # if initial_time:
        #     t = np.arange(-initial_time, time - initial_time, 1./freq_sampling) % period
        #     s1 = sign.Signal(amplitude, t, f0, bandwidth, period, phi_0, freq_sampling).signal

        #     t = np.arange(0, time, 1./freq_sampling) % period
        #     s2 = sign.Signal(amplitude, t, f0, bandwidth, period, phi_0, freq_sampling).signal
        #     freq = sp.fft(s1*s2)
        #     freq[180:-180] = 0
        #     plt.plot(np.real(sp.ifft(freq)))
        #     # print(np.angle(sp.fft(s1*s2)))
        #     # plt.plot(abs(sp.fft(s1)))
        #     plt.grid()
        #     plt.show()
        return sign.Signal(amplitude, t, f0, bandwidth, period, phi_0, freq_sampling)

    @property
    def real_b(self):
        return self.__real_b


class Radar:

    def __init__(self, amp=1., phi=0., max_freq_lpf=10e3, adc_freq=40E3):
        self.__initial_phase = phi
        self.__r = 50
        self.__time = common.SignalProperties.Time
        self.__adc_freq = adc_freq
        self.__tx_signal = None

        self.__signal_gen = SignalGenerator()
        self.__lpf = LowPassFilter(max_freq_lpf, adc_freq)
        self.__deramped_phase = 0

        # This is the power of the central frequency, it was measured when I went to cordoba
        self.__tx_power = 1E-3 * np.power(10, 11.87/10)
        rx_power = 1E-3 * np.power(10, -21.91/10)
        distance = 1.427
        wavelength = common.SignalProperties.C / 2450E6
        self.__gt_gr = rx_power * (4*np.pi*distance)**2 / (self.__tx_power*wavelength**2)

    def measure_distance_to_target(self, dist):
        """
        this method obtains the deramped ideal phase from the distance to target
        """
        k = 2*np.pi*common.SignalProperties.B/common.SignalProperties.T
        tau = 2*dist / common.SignalProperties.C
        wc = 2*np.pi*common.SignalProperties.F0
        self.__deramped_phase = format_phase(wc*tau - k*tau*common.SignalProperties.T/2 - k*tau**2/2)

    def transmit(self):
        # The signal power is the same for a chirp or for a sin, so the voltage is the same for one or the other
        # function and the power relation between the voltage peak and power is P = v**2/2
        voltage = np.sqrt(2*self.__tx_power * self.__gt_gr)
        self.__tx_signal = self.__signal_gen.generate_chirp(voltage, self.__time, self.__initial_phase)
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
        # print("offsets", offset, offset2, calc1, calc2)
        return offset/2 if abs(offset) < 0.05 else offset2

    def process_reception(self, signal):
        previous_half_length = int(signal.length/2)
        amount_points = int(np.exp2(np.ceil(np.log2(signal.length))+3))
        if amount_points/signal.length < 8.17:
            raise Exception("The padding relation should be bigger than 8.17, otherwise DeltaPhi is bigger than 2pi")

        frequency = sp.fft(np.blackman(signal.length) * signal.signal, amount_points)[:amount_points/2]*2/signal.length
        n = np.argmax(abs(frequency))

        """
        # This makes the signal periodical and after that makes the roll calculating the signals frequency
        initial_pos, final_pos = signalProcessor.SignalProcessor.make_periodical(signal)
        half_length = previous_half_length - initial_pos
        # frequency = sp.fft(np.roll(signal.signal, - half_length), amount_points)[:amount_points/2]*2/signal.length
        frequency = sp.fft(np.blackman(signal.length) * np.roll(signal.signal, - half_length), amount_points)[:amount_points/2]*2/signal.length
        n = np.argmax(abs(frequency))
        frequency2 = sp.fft(signal.signal, amount_points)[:amount_points/2]*2/signal.length
        """

        # half_length = signal.length//2
        # amount_points = int(np.exp2(np.ceil(np.log2(signal.length))+3))
        # frequency2 = sp.fft(np.roll(np.blackman(signal.length) * signal.signal, -half_length), amount_points)[:amount_points/2]*2/signal.length
        # frequency = sp.fft(np.blackman(signal.length) * np.roll(np.blackman(signal.length) * signal.signal, -half_length), amount_points)[:amount_points/2]*2/signal.length
        
        # print(n, np.argmax(abs(frequency2)), "P:", amount_points/signal.length)
        # print("P:", amount_points/signal.length)

        # plt.plot(np.blackman(signal.length) * signal.signal)
        # plt.plot(np.blackman(signal.length) * np.roll(np.blackman(signal.length) * signal.signal, -half_length))
        # plt.plot(signal.signal)
        # plt.show()

        # FFT resolution is equal to Fs/NFFT
        # d_f = np.argmax(abs(frequency))*self.__adc_freq/amount_points
        # # print()
        # # print("Measurements:")
        # # print("----------------------------------------------------")
        # # print("Frequency to target:\t", d_f, "\tPosition:", np.argmax(abs(frequency)))

        # # distance = common.SignalProperties.T * d_f * common.SignalProperties.C/(2*self.__signal_gen.real_b)
        # # delta_r = common.SignalProperties.C/2/self.__signal_gen.real_b * signal.length/amount_points

        # distance = common.SignalProperties.T * d_f * common.SignalProperties.C/(2*common.SignalProperties.B)
        # delta_r = common.SignalProperties.C/2/common.SignalProperties.B * signal.length/amount_points
        # # print("Distance to target:\t", distance, "\tDelta distance:", delta_r)

        # d_t = d_f*common.SignalProperties.T/common.SignalProperties.B
        # # print("Round trip time:\t", d_t)

        # k = 2*np.pi*common.SignalProperties.B/common.SignalProperties.T
        # wc = 2*np.pi*common.SignalProperties.F0
        # # phase = format_phase(wc * d_t - k*d_t**2)
        # # In this case i'm adding the second component because I didn't rotate the signal
        # phase = format_phase(wc * d_t - k*d_t*common.SignalProperties.T/2 - k*d_t**2/2)
        # phase2 = format_phase(wc * d_t - k*d_t**2/2)

        # first = wc * d_t
        # second = - k*d_t*common.SignalProperties.T/2
        # third = - k*d_t**2/2

        # k =  2*np.pi*common.SignalProperties.B/common.SignalProperties.T
        # tau = common.SignalProperties.T * d_f/common.SignalProperties.B
        # self.__deramped_phase = format_phase(wc*tau - k*tau*common.SignalProperties.T/2 - k*tau**2/2)

        # print()
        # print("Phase components:", format_phase(first), format_phase(second), format_phase(third))
        # print("Expected Phase:\t\t", format_phase(first + second + third), "\t", format_phase(first + third))
        # print("Received Phase:\t\t", format_phase(np.angle(frequency)[np.argmax(abs(frequency))]), "\t", format_phase(np.angle(frequency2)[np.argmax(abs(frequency2))]))
        # print("Received Phase:\t\t", format_phase(np.angle(frequency)[np.argmax(abs(frequency))]))
        # print("Der Phase from dist:\t", self.__deramped_phase)
        # print("Normalized Phase:\t", format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - phase), "\t", format_phase(np.angle(frequency2)[np.argmax(abs(frequency2))] - phase2))
        # print("Final Target's phase:\t", format_phase(self.__deramped_phase - np.angle(frequency)[np.argmax(abs(frequency))]), '\tDeg:', np.rad2deg(self.__deramped_phase - np.angle(frequency)[np.argmax(abs(frequency))]))

        target_gain = signal.power
        target_phase = np.rad2deg(format_phase(self.__deramped_phase - np.angle(frequency)[np.argmax(abs(frequency))]))
        return target_gain, target_phase
        # print("Received Phase:\t", format_phase(np.angle(frequency)[np.argmax(abs(frequency))]), "\t", format_phase(np.angle(frequency2)[np.argmax(abs(frequency))]))
        # print("Normalized Phase:\t", format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - phase), "\t", format_phase(np.angle(frequency2)[np.argmax(abs(frequency))] - phase2))


        # What will happen if I change the way of calculating the phase 
        # print()
        # final_ph = format_phase(np.angle(frequency)[np.argmax(abs(frequency))] - phase)
        # print("Target's phase:\t\t", final_ph)
        # print()
        
        # # print(signal.wavelength, final_ph, 4*np.pi)
        # fine_r = signal.wavelength*final_ph/(4*np.pi)
        # print("Fine distance:\t\t", fine_r)
        # print("Final distance:\t\t", fine_r + distance)

        # # Now I'm calculating with every phas's parameter
        # a = 2*k/common.SignalProperties.C**2
        # b = k*common.SignalProperties.T/common.SignalProperties.C - 4*np.pi*common.SignalProperties.F0/common.SignalProperties.C
        # # b = - 4*np.pi*common.SignalProperties.F0/common.SignalProperties.C
        # c = final_ph
        # first = b/(2*a)
        # second = c/a
        # print()
        # print("r1", (-b+np.sqrt(b**2 - 4*a*c))/(2*a), (-b-np.sqrt(b**2 - 4*a*c))/(2*a))
        # print("r1", -first + np.sqrt(first**2 - second), -first - np.sqrt(first**2 - second) )
        # print("Final distance:\t\t", -first - np.sqrt(first**2 - second) + distance)

        # a = k/2
        # # b = k*common.SignalProperties.T/2 - wc
        # b = - wc
        # c = final_ph
        # first = b/(2*a)
        # second = c/a
        # print()
        # print("r1", (-b+np.sqrt(b**2 - 4*a*c))/(2*a), (-b-np.sqrt(b**2 - 4*a*c))/(2*a))
        # print("r1", -first + np.sqrt(first**2 - second), -first - np.sqrt(first**2 - second) )
        # print("final distance from tau:", (-first - np.sqrt(first**2 - second))+ d_t)
        # """
        # I don't remember where I've obtained the following lines
        # delta_f = self.__calculate_gain(np.argmax(abs(frequency)), frequency)
        # d_f = (np.argmax(abs(frequency)) + delta_f)*self.__adc_freq/signal.length
        # distance = common.SignalProperties.T * d_f*common.SignalProperties.C/(2*self.__signal_gen.real_b)
        # print("Measured frequency to target:", d_f)
        # print("Measured distance to target:", distance)
        # """
        # plt.plot(np.abs(frequency2)[400:800], label="frequency2")
        # plt.plot(np.abs(frequency)[400:800], label="frequency")
        # plt.legend(loc=4)
        # plt.grid()
        # plt.show()


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
        signal = sign.Signal(signal1.amplitude*signal2.amplitude, np.array([1, 2]), fs=signal1.freq_sampling)
        signal.signal = signal1.signal * signal2.signal

        return signal


class LowPassFilter:

    def __init__(self, max_freq, adc_freq):
        self.__upper_freq = max_freq
        self.__adc_freq = adc_freq

    def butter_lowpass(self, cutoff, fs, order=4):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(self, data, cutoff, fs, order=4):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y


    def filter_signal(self, signal):
        """
        :param signal: the input signal to filter
        :return:
        """
        output_signal =  self.butter_lowpass_filter(signal.signal, self.__upper_freq, signal.freq_sampling)[::signal.freq_sampling/self.__adc_freq]

        signal_filtered = sign.Signal(signal.amplitude, np.array([1, 2]), fs=self.__adc_freq)
        signal_filtered.signal = output_signal

        return signal_filtered

        # amount_points = int(np.exp2(np.ceil(np.log2(signal.length))))
        # freq = sp.fft(signal.signal, amount_points)

        # n_max = self.__upper_freq*signal.length/signal.freq_sampling
        # freq[n_max:-n_max] = 0

        # samples = self.__adc_freq*len(freq)/signal.freq_sampling/2 + 1

        # output_signal = np.real(sp.ifft(np.concatenate((freq[:samples], freq[-samples:])))
        #                         )*self.__adc_freq/signal.freq_sampling

        # signal_filtered = sign.Signal(signal.amplitude, np.array([1, 2]), fs=self.__adc_freq)
        # signal_filtered.signal = output_signal[:signal.length*self.__adc_freq/signal.freq_sampling]

        # return signal_filtered


class Medium:

    def __init__(self, obj):
        """
        :param obj: the illuminated object
        :return:
        """
        self.__real_f0 = 2450E6
        self.__object = obj
        self.__attenuation = lambda x: 1/((4*np.pi)**3 * x**4)

    def propagate_signal(self, signal, dist_to_obj=5.):
        d_t = 2.*dist_to_obj/common.SignalProperties.C
        # print('Real round-trip time:\t', d_t)
        sign_gen = SignalGenerator()

        gain = self.__object.gain * np.power(signal.wavelength, 2) * self.__attenuation(dist_to_obj)
        # The following rx_voltage was chosen in order to have a signal power equal to signal.power*gain. I have no analytical equation for it.
        rx_voltage = 10.13375451139e-10
        rx_ph = format_phase(self.__object.phase + signal.phi_0)
        return sign_gen.generate_chirp(rx_voltage, common.SignalProperties.Time, rx_ph, initial_time=d_t)


class Object:

    def __init__(self, gain, phase):
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

    distance = common.Distance_to_Target
    radar.measure_distance_to_target(distance)

    medium = Medium(Object(common.TargetProperties.Gain, common.TargetProperties.Phase))
    # print()
    # print("Target properties:")
    # print("----------------------------------------------------")
    # print("Distance to target:\t", common.Distance_to_Target)
    # print("Target phase:\t\t", common.TargetProperties.Phase)
    rx_sign = medium.propagate_signal(tx_signal, dist_to_obj=common.Distance_to_Target)

    output = radar.receive(rx_sign)

    print(radar.process_reception(output))
    exit(0)
