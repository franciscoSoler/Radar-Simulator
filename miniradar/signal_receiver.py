
import sys
import common
import signal_base as sign
try:
    import pyaudio
except ImportError:
    sys.exit('You need pyaudio installed to run this demo.')


class SignalReceiver:

	def __init__(self):
		self.__stream = None
		self.__num_samples = 8200
		self.__sampling_rate = 40000


	def __get_normalized_audio(self):
	    if self.__stream is None:
	        pa = pyaudio.PyAudio()
	        self.__stream = pa.open(format=pyaudio.paInt16, channels=2, rate=self.__sampling_rate,
	                          		input=True, frames_per_buffer=self.__num_samples)
	    audio_data = fromstring(self.__stream.read(self.__num_samples), dtype=short)
	    audio_data = reshape(audio_data, (self.__num_samples, 2))

	    return audio_data / 32768.0

	def get_audio_data(self, num_samples):
	    audio_data = self.__get_normalized_audio()

	    flanks = get_stream_flanks(audio_data[:, 1])

	    # I deleted the first and the last period, todo: is this necessary???
	    rising_flanks = map(lambda x: x + CUT/2, flanks[2:-2:2])

	    if flanks:
	        length = int(round(np.mean(map(lambda x, y: x-y, flanks[1::2], flanks[0::2]))))
	        normalized_data = np.mean([audio_data[i:i+length] for i in rising_flanks], axis=0)
	    else:
	        length = num_samples
	        normalized_data = audio_data[0:length]

	    return normalized_data[:,0]#, length, flanks
