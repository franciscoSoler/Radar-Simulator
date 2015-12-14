import scipy as sp
import numpy as np
import matplotlib.pyplot as plt


class SignalProcessor:

    def __init__(self):
        pass

    @staticmethod
    def make_periodical(signal):
        """
        this method cuts the input signal in order to transform it in periodical.
        :param signal: the input signal
        :return:
        """
        amount_points = int(np.exp2(np.ceil(np.log2(signal.length))))
        period_length = amount_points / np.argmax(abs(sp.fft(signal.signal, amount_points)))

        initial_pos = int(period_length/2)
        last_pos = -int(period_length/2)
        delta = 5

        initial_slope = signal.signal[delta + initial_pos] - signal.signal[initial_pos] > 0
        final_slope = signal.signal[last_pos] - signal.signal[last_pos - delta] > 0

        initial_sign = signal.signal[initial_pos] > 0
        final_sign = signal.signal[last_pos] > 0

        if initial_slope ^ final_slope:
            # in this case the slope of the initial/final signal is not the same
            last_pos -= int(period_length/2)

        if initial_sign ^ final_sign:
            # in this case the sign of the initial/final signal is not the same
            last_pos -= int(3*period_length/4) if final_sign ^ final_slope else int(period_length/4)

        # now I have to move through the signal searching for the closest value to the initial point
        movement = 1 if initial_slope ^ (signal.signal[last_pos] > signal.signal[initial_pos]) else -1

        def calc_distance(x):
            return abs(x - signal.signal[initial_pos])
        while calc_distance(signal.signal[last_pos]) > calc_distance(signal.signal[last_pos + movement]):
            last_pos += movement

        # now I have to remove the last point if necessary
        last_pos -= 0 if initial_slope ^ (signal.signal[last_pos] > signal.signal[initial_pos]) else 1

        signal.signal = signal.signal[initial_pos:last_pos]
        return initial_pos, last_pos
