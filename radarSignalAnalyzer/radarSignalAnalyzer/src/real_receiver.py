try:
    import pyaudio
except ImportError:
    sys.exit('You need pyaudio installed to run this demo.')

import radarSignalAnalyzer.src.signal_receiver as receiver


class RealReceiver(receiver.SignalReceiver):
    """Class that reads frames of audio from the mic."""

    def __init__(self):
        super(RealReceiver, self).__init__(signal_in_channel_one=True)
        self.__pa = None

    def _get_audio(self):
        """Read a block of bytes from the stream."""
        if self._stream is None:
            self.__pa = pyaudio.PyAudio()
            self._stream = self.__pa.open(format=pyaudio.paInt16, channels=2, rate=int(self._sampling_rate),
                                    input=True, frames_per_buffer=self._num_samples)

        return self._stream.read(self._num_samples)

    def rewind(self):
        """Rewind the opened stream."""
        raise Exception("this method cannot be called")

    def stop(self):
        """Close the opened stream."""
        self._stream.stop_stream()
        self._stream.close()
        self.__pa.terminate()
        self._stream = None
        self.__pa = None
