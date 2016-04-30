import signal_receiver as receiver
import wave


class FileReceiver(receiver.SignalReceiver):

    def __init__(self):
        super(FileReceiver, self).__init__()
        self.__filename = "radar260cmToTarget.wav"
        # self.__filename = "radar270withAndWithoutTarget.wav"


    def _get_audio(self):
        if self._stream is None:
            self._stream = wave.open(self.__filename, 'rb')
            self._sampling_rate = self._stream.getframerate()
        return self._stream.readframes(self._num_samples)
