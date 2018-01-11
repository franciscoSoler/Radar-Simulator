from PyQt5 import QtCore
import numpy as np
import scipy as sp
import enum
import src.real_receiver as r_receiver
import src.file_receiver as f_receiver
import src.signal_processor as signal_processor
import src.distance_calculator as calculator
import src.common as common
import src.signal_base as sign

np.seterr(all='raise')


def get_mean_std(num_sample, sample, mean, std):
        """
        This method shows the mean and std value from the targets phase.
        It's assumed a gaussian distribution, so the shown value is mean +- 3std
        """

        n = num_sample - 1
        new_mean = (n * mean + sample) / num_sample

        if n == 0:
            return new_mean, 0

        # new_std = np.sqrt(((n - 1) * std**2 + (sample - new_mean)**2) / n)
        new_std = np.sqrt(((sample - new_mean)*(sample - mean) + (n - 1)*std**2) / n)

        return new_mean, new_std


def w2db(w):
    return -99999999999 if w == 0 else 10*np.log10(w)


def v2db(v):
    return 2*w2db(abs(v))


def db2v(dbs):
    return 10**(dbs/20)


class Measurement(enum.Enum):
    Gain = 1
    Phase = 2
    Distance = 3


class Controller(QtCore.QObject):

    update_data = QtCore.pyqtSignal(float, list, float, list, list, float, float, float)

    def __init__(self, max_freq, real_time=True):
        super(Controller, self).__init__()
        self.__measure_clutter = False
        self.__calculator = calculator.DistanceCalculator()

        self.__max_freq = max_freq
        self.__receiver = None
        self.__num_samples = None
        self.__clutter = None
        self.__freq_points = None
        self.__quantity_freq_samples = None

        self.set_real_time_mode(real_time)
        self.__samples_to_cut = 0  # this variable cuts the beginning of the signal in order to delete some higher frequencies,
                                    # 30m = 0.008 samples --> no necesito cortar nada de nada

        self.__use_external_clutter = False
        self.__ext_clutter = None

        # Radar Properties [dBm]
        tx_power = 11.87
        rx_power = -21.91

        # Distance [m]
        distance = 1.427
        wavelength = common.C / common.F0
        gt_gr = rx_power - tx_power + v2db(4*np.pi*distance/wavelength)

        rf_lossess = -5
        cable_losses = -1.06392
        lna_gain = 14
        mixer_gain = -5.5
        lpf_gain = 9
        radar_to_mic = v2db(2/3)
        self.__rf_chain_gain = tx_power + gt_gr + 2*cable_losses + rf_lossess + lna_gain + mixer_gain + lpf_gain + radar_to_mic

        antenna_delay = 0.31688E-9

        cable_length = 0.365
        cable_vel = common.C * 0.67
        cable_delay = cable_length/cable_vel
        self.__cable_phase = signal_processor.format_phase(cable_delay*common.F0*360)

        rx_length = 0.07
        rx_delay = rx_length/cable_vel
        self.__componens_delay = 2 * (antenna_delay + cable_delay) + rx_delay

        self.__freq_cut = 250
        self.__subtract_medium_phase = True
        self.__distance_from_gui = 0
        self.__use_distance_from_gui = 0

        self.__n = 0
        self.__measurements = {me: (0, 0) for me in Measurement}
        self.__mean_gain = 0
        self.__std_gain = 0
        self.__mean_phase = 0
        self.__std_phase = 0
        self.__mean_dist = 0
        self.__std_dist = 0
        self.__cut = np.pi

        self.__real_time = real_time
        self.__stop = True

    def __initialize_singal_properties(self):
        self.__num_samples = self.__receiver.get_num_samples_per_period()

        while not self.__num_samples:
            self.__num_samples = self.__receiver.get_num_samples_per_period()

        self.__clutter = sign.Signal([0]*self.__num_samples)
        self.__freq_points = int(np.exp2(np.ceil(np.log2(self.__num_samples))+7))
        self.__quantity_freq_samples = self.__max_freq*self.__freq_points//self.__receiver.sampling_rate

    @property
    def signal_length(self):
        # TODO I have to delete this property, it's not a property
        return self.__num_samples - self.__samples_to_cut

    @property
    def freq_length(self):
        return self.__quantity_freq_samples

    def get_signal_range(self):
        d_t = 1/self.__receiver.sampling_rate
        return np.arange(0, d_t*self.signal_length, d_t)

    def get_frequency_range(self):
        d_f = self.__receiver.sampling_rate/self.__freq_points
        return np.arange(0, d_f*self.__freq_points//2, d_f)[:self.__quantity_freq_samples]

    def get_disance_from_freq(self, freq):
        signal = self.__receiver.get_audio_data(self.__num_samples)
        return signal.period * freq*common.C/(2*signal.bandwidth)

    def __calculate_targets_properties(self, signal, frequency, distance):
        gain = w2db(2*signal.power * (4*np.pi)**3 * distance**4 / signal.wavelength**2) - self.__rf_chain_gain

        # This part is for calculating the distances phase shift
        k = 2*np.pi*signal.bandwidth/signal.period
        tau = 2*distance / common.C
        # tau += self.__componens_delay if self.__use_distance_from_gui else 0
        wc = 2*np.pi*signal.central_freq

        antenna_phase = 2 * 192.15

        rtt_ph = signal_processor.format_phase(wc*tau - k*tau*signal.period/2 - k*tau**2/2 + 2*self.__cable_phase + antenna_phase)
        ang = np.angle(frequency)[np.argmax(abs(frequency))]

        return gain, signal_processor.format_phase(ang - rtt_ph if self.__subtract_medium_phase else ang), rtt_ph

    def __process_reception(self, signal):
        self.__n += 1
        signal.cut(self.__samples_to_cut)
        frequency, freq_sampling = signal.obtain_spectrum(self.__freq_points)
        f_min = self.__freq_cut*self.__freq_points//self.__receiver.sampling_rate
        d_f = (f_min+np.argmax(abs(frequency[f_min:])))*freq_sampling/self.__freq_points

        # calculated_distance = signal.period * d_f*common.C/(2*signal.bandwidth)
        calculated_distance = (signal.period * d_f / signal.bandwidth - self.__componens_delay) * common.C/2

        distance = self.__distance_from_gui if self.__use_distance_from_gui else calculated_distance
        delta_r = common.C/2/signal.bandwidth * signal.length/self.__freq_points
        # d_t = d_f*signal.period/signal.bandwidth
        # k = np.pi*signal.bandwidth/signal.period
        # phase = signal_processor.format_phase(2*np.pi*signal.central_freq * d_t - k*d_t**2)
        # if np.argmax(abs(frequency)) > self.__quantity_freq_samples:
        #     raise Exception("el módulo máximo de la frecuencia dio en valires de frecuencia negativa en vez de \
        #         positiva. índice: {}".format(np.argmax(abs(frequency))))
            # If this exception is raised, please change the following lines with:
            # np.argmax(abs(frequency[:self.__quantity_freq_samples]))

        gain, target_phase, rtt_ph = self.__calculate_targets_properties(signal, frequency, distance)

        gain_to_tg = w2db(1/(np.power(4*np.pi, 2) * distance**4) if distance else float("inf"))

        if self.__n == 1:
            self.__cut = 0 if target_phase > np.pi/2 and target_phase < np.pi else 2*np.pi if target_phase > -np.pi and target_phase < -np.pi/2 else np.pi

        calc_dist, tg_gain, tg_ph = self.__get_final_measurements(calculated_distance, gain, np.rad2deg(signal_processor.format_phase(target_phase, self.__cut)))

        self.update_data.emit(round(d_f, 3), calc_dist, round(delta_r, 6), tg_gain, tg_ph, round(gain_to_tg, 8),
                              round(np.rad2deg(rtt_ph), 1), round(distance, 4))

        if signal.length > self.signal_length:
            data = signal.signal[:self.signal_length]
        else:
            data = np.concatenate((signal.signal, [0]*(self.signal_length-signal.length)))

        return data, abs(frequency[:self.__quantity_freq_samples]), np.rad2deg(target_phase)

    def __get_final_measurements(self, distance, gain, phase):
        """
        This method shows the mean and std value from several measurements.
        It's assumed a gaussian distribution, so the shown value is mean +- 3std
        """
        self.__measurements[Measurement.Distance] = get_mean_std(self.__n, distance, *self.__measurements[Measurement.Distance])
        self.__measurements[Measurement.Gain] = get_mean_std(self.__n, gain, *self.__measurements[Measurement.Gain])
        self.__measurements[Measurement.Phase] = get_mean_std(self.__n, phase, *self.__measurements[Measurement.Phase])

        return [round(x + 2*i*x, 3) for i,x in enumerate(self.__measurements[Measurement.Distance])], \
               [round(x + 2*i*x, 4) for i,x in enumerate(self.__measurements[Measurement.Gain])], \
               [round(x + 2*i*x, 1) for i,x in enumerate(self.__measurements[Measurement.Phase])]

    def run(self, t=0):
        signal = self.__receiver.get_audio_data(self.__num_samples)

        if self.__measure_clutter:
            self.__measure_clutter = False

            if self.__use_external_clutter:
                self.__clutter.signal = self.__ext_clutter.signal*signal.applied_volume
            else:
                self.__clutter.signal = signal.signal

            self.__clutter.applied_volume = signal.applied_volume
            self.__clutter.frequency_sampling = signal.frequency_sampling

        signal.subtract_signals(self.__clutter)

        yield self.__process_reception(signal)

    def remove_clutter(self):
        self.__measure_clutter = True

    def restore_clutter(self):
        self.__clutter.signal = np.zeros(self.__clutter.length)

    def set_distance_from_gui(self, distance):
        self.__use_distance_from_gui = True
        self.__distance_from_gui = distance
        self.reset_statistics()

    def remove_distance(self):
        if self.__use_distance_from_gui:
            self.reset_statistics()

        self.__use_distance_from_gui = False

    def reset_statistics(self):
        self.__n = 0
        self.__measurements = {me: (0, 0) for me in Measurement}

    def rewind_audio(self):
        self.reset_statistics()
        self.__receiver.rewind()

    def set_auto_rewind(self, auto):
        self.__receiver.auto_rewind = auto

    def set_volume(self, volume):
        self.__receiver.volume = db2v(volume)

    def reset_volume(self):
        self.__receiver.reset_volume()

    def increase_volume(self):
        increment = 1
        self.__receiver.modify_volume(db2v(increment))
        return increment

    def decrease_volume(self):
        decrement = 1
        self.__receiver.modify_volume(db2v(-decrement))
        return decrement

    def use_external_signal(self, file_path):
        self.__receiver.track = file_path
        self.reset_statistics()
        self.__initialize_singal_properties()

    def use_external_clutter(self, file_path):
        receiver = f_receiver.FileReceiver(file_path)
        self.reset_statistics()
        self.__ext_clutter = receiver.get_audio_data(self.__num_samples)
        self.__use_external_clutter = True
        receiver.stop()

    def stop_using_external_clutter(self):
        self.__use_external_clutter = False

    def set_real_time_mode(self, real_time=True):
        if self.__receiver is not None:
            self.__receiver.stop()

        self.__receiver = r_receiver.RealReceiver() if real_time else f_receiver.FileReceiver()
        self.reset_statistics()
        self.__initialize_singal_properties()
