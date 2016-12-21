from abc import ABCMeta, abstractmethod

import common
import signal_base as sign
import numpy as np
import matplotlib.pyplot as plt


class SignalReceiver(metaclass=ABCMeta):

    def __init__(self):
        self._stream = None
        self._num_samples = 8200
        self._sampling_rate = 40000

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @staticmethod
    def __get_stream_flanks(stream, delay_time=common.DELAY_TIME, window=0.5):
        win = (max(stream) - min(stream)) / 8
        final_window = win if win < window else window
        flanks = [i for i, value in enumerate(stream) if abs(stream[i-1] - value) > final_window and i > 0]
        res = sum([[flanks[i-1], val] for i, val in enumerate(flanks) if val - flanks[i - 1] > delay_time], [])
        return res

    @abstractmethod
    def _get_audio():
        pass

    def __get_normalized_audio(self):
        audio_data = np.fromstring(self._get_audio(), dtype=np.short)
        audio_data = np.reshape(audio_data, (self._num_samples, 2))
        return audio_data / 32768.0

    def get_num_samples_per_period(self):
        num_samples = 0
        flanks = self.__get_stream_flanks(self.__get_normalized_audio()[:, 1])

        if len(flanks) > 5:
            num_samples = int(round(np.mean(list(map(lambda x, y: x-y, flanks[1::2], flanks[0::2])))))
        return num_samples

    def get_audio_data(self, num_samples):
        audio_data = self.__get_normalized_audio()

        flanks = self.__get_stream_flanks(audio_data[:, 1])

        if flanks:
            length = int(round(np.mean(list(map(lambda x, y: x-y, flanks[1::2], flanks[0::2])))))
            normalized_data = np.mean([audio_data[i:i+length] for i in flanks[0::2]], axis=0)
        else:
            length = num_samples
            normalized_data = audio_data[0:length]

        return sign.Signal(normalized_data[:,0], fs=self._sampling_rate)
