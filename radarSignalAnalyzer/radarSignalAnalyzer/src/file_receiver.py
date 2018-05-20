import wave
import os

import radarSignalAnalyzer.src.signal_receiver as receiver


class FileReceiver(receiver.SignalReceiver):
    """Class that reads frames of audio from a file."""

    def __init__(self, filename=''):
        super(FileReceiver, self).__init__()
        self.__filename = "measurements/cornerReflector/dist1_HH.wav" if not filename else filename
        self.__auto_rewind = False

    @property
    def track(self):
        """Return the path of the opened audio file."""
        return self.__filename

    @track.setter
    def track(self, filename):
        """
        Set a new audio file to reproduce.

        :param filename: path representing the filename to open.
        :raises Exception: when the file to open does not exist.
        """
        if not os.path.isfile(filename):
            raise Exception('Nonexistent audio file. Received {}'.format(filename))

        self.stop()
        self.__filename = filename

    @property
    def auto_rewind(self):
        """Return the auto rewind state."""
        return self.__auto_rewind

    @auto_rewind.setter
    def auto_rewind(self, auto):
        """
        Set a new auto rewind state.

        :param auto: Boolean indicating if the auto rewind state is on/off.
        :raises Exception: when the parameter auto is not boolean.
        """
        if not isinstance(auto, bool):
            raise Exception('Auto rewind state is not boolean. Received {}'.format(auto))

        self.__auto_rewind = auto

    def _get_audio(self):
        """Read a block of bytes from the stream."""
        if self._stream is None:
            self._stream = wave.open(self.__filename, 'rb')
            self._sampling_rate = self._stream.getframerate()

        frames = self._stream.readframes(self._num_samples)
        if self.__auto_rewind and not self._check_read_samples(frames, formatted=False):
            self.rewind()
            frames = self._get_audio()
        return frames

    def rewind(self):
        """Rewind the opened stream."""
        self._stream.rewind()

    def stop(self):
        """Close the opened stream."""
        if self._stream is not None:
            self._stream.close()

        self._stream = None
