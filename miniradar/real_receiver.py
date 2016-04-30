import signal_receiver as receiver
try:
    import pyaudio
except ImportError:
    sys.exit('You need pyaudio installed to run this demo.')


class RealReceiver(receiver.SignalReceiver):

    def __init__(self):
        super(RealReceiver, self).__init__()

    def _get_audio(self):
        if self._stream is None:
            pa = pyaudio.PyAudio()
            self._stream = pa.open(format=pyaudio.paInt16, channels=2, rate=self._sampling_rate,
                                    input=True, frames_per_buffer=self._num_samples)

        return self._stream.read(self._num_samples)
