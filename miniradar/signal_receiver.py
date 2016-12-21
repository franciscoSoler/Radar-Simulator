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

        # Deleting glitches
        stream_2 = [(stream[i-1] + stream[i+1])/2
                    if stream[i] > stream[i-1] + final_window and stream[i] > stream[i+1] + final_window else stream[i]
                    for i in range(1, len(stream)-1)]

        # The first and last stream values are missing in stream_2.
        sstream = [stream[0]] + stream_2 + [stream[-1]]

        # Obtaining every flank in the stream
        flanks = [i for i, value in enumerate(sstream) if abs(sstream[i-1] - value) > final_window and i > 0]

        # Ordering flanks by descending and ascending
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
