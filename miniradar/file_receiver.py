import signal_receiver as receiver
import wave


class FileReceiver(receiver.SignalReceiver):

    def __init__(self):
        super(FileReceiver, self).__init__()
        # self.__filename = "radar260cmToTarget.wav"
        # self.__filename = "radar270withAndWithoutTarget.wav"
        self.__filename = "../measurements/radar distances/dist5TxHRxH.wav"
        self.__auto_rewind = False

    @property
    def auto_rewind(self):
        return self.__auto_rewind

    @auto_rewind.setter
    def auto_rewind(self, auto):
        self.__auto_rewind = auto

    def _get_audio(self):
        if self._stream is None:
            self._stream = wave.open(self.__filename, 'rb')
            self._sampling_rate = self._stream.getframerate()

        frames = self._stream.readframes(self._num_samples)
        if self.__auto_rewind and not self._check_read_samples(frames, formatted=False):
            self.rewind()
            frames = self._get_audio()
        return frames

    def rewind(self):
        self._stream.rewind()
