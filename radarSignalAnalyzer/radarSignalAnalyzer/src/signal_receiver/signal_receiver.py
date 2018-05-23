from abc import ABCMeta, abstractmethod
import numpy as np
import logging

import radarSignalAnalyzer.src.common as common
import radarSignalAnalyzer.src.signal_base as sign


class SignalReceiver(metaclass=ABCMeta):

    def __init__(self, signal_in_channel_one=False):
        self._logger = logging.getLogger(__name__)
        self._stream = None
        self._num_samples = 8200
        self._sampling_rate = common.Sampling_rate
        self.__normalization_value = 32768.0
        self.__volume = 1
        if signal_in_channel_one:
            self.__signal_channel = 1
            self.__sync_channel = 0

        else:
            self.__signal_channel = 0
            self.__sync_channel = 1

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @property
    def volume(self):
        """Get the volume in dBs."""
        return self.__volume

    @volume.setter
    def volume(self, vol):
        """
        Sets the volume.

        :param vol: float number in dBs.
        """
        self.__volume = common.db2v(vol)

    def modify_volume(self, increment):
        """
        Increase or decrease the volume.

        :param increment: float number in dBs.
        """
        self.__volume *= common.db2v(increment)

    def __get_stream_flanks(self, stream, delay_time=common.DELAY_TIME, window=0.5):
        win = (max(stream) - min(stream)) / 8
        final_window = win if win < window else window
        self._logger.debug('Final window to find flanks: %f', final_window)
        # Deleting glitches
        stream_2 = [(stream[i-1] + stream[i+1])/2
                    if stream[i+1] + final_window < stream[i] > stream[i-1] + final_window else stream[i]
                    for i in range(1, len(stream)-1)]

        # The first and last stream values are missing in stream_2.
        sstream = [stream[0]] + stream_2 + [stream[-1]]

        # Obtaining every flank in the stream
        flanks = [i + 1 for i, value in enumerate(sstream[1:]) if abs(sstream[i] - value) > final_window]

        # Ordering flanks by descending and ascending
        res = sum([[flanks[i-1], val] for i, val in enumerate(flanks) if val - flanks[i - 1] > delay_time], [])
        self._logger.debug('Flanks found: {}'.format(res))
        return res

    @abstractmethod
    def _get_audio(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def _check_read_samples(self, frames, formatted=True):
        channels = 2
        data_size = 1 if formatted else 2
        return True if len(frames) == self._num_samples * channels * data_size else False

    def __get_normalized_audio(self):
        audio_data = np.fromstring(self._get_audio(), dtype=np.short)
        if not self._check_read_samples(audio_data):
            message = "Audio stream's length found, {}, is different from the expected, {}.".format(len(audio_data),
                self._num_samples)
            self._logger.error(message)
            raise EOFError(message)

        return audio_data.reshape(self._num_samples, 2)/self.__normalization_value

    def reset_volume(self):
        self.__volume = 1

    def get_num_samples_per_period(self):
        num_samples = 0
        flanks = self.__get_stream_flanks(self.__get_normalized_audio()[:, self.__sync_channel])

        if len(flanks) > 5:
            num_samples = int(round(np.mean(list(map(lambda x, y: x-y, flanks[1::2], flanks[0::2])))))
        self._logger.debug('Averaged samples per period in the signal = %d', num_samples)
        return num_samples

    @abstractmethod
    def rewind(self):
        pass

    def get_audio_data(self, num_samples):
        audio_data = self.__get_normalized_audio()

        flanks = self.__get_stream_flanks(audio_data[:, self.__sync_channel])

        if flanks:
            length = int(round(np.mean(list(map(lambda x, y: x-y, flanks[1::2], flanks[0::2])))))
            self._logger.debug('Samples between flanks: {}'.format(length))
            chunk_length = len(audio_data)
            normalized_data = np.mean([audio_data[i:i+length] for i in flanks[0::2] if i + length <= chunk_length],
                axis=0)

        else:
            length = num_samples
            normalized_data = audio_data[0:length]

        return sign.Signal(normalized_data[:, self.__signal_channel]*self.__volume, fs=self._sampling_rate, 
                           applied_volume=self.__volume)
