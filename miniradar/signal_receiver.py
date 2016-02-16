
import sys
import common
import signal_base as sign
import numpy as np
try:
    import pyaudio
except ImportError:
    sys.exit('You need pyaudio installed to run this demo.')

DELAY_TIME = 100


class SignalReceiver:

	def __init__(self):
		self.__stream = None
		self.__num_samples = 8200
		self.__sampling_rate = 40000

	@staticmethod
	def __get_stream_flanks(stream, delay_time=DELAY_TIME, window=0.5):
	    win = (max(stream) - min(stream)) / 4
	    final_window = win if win > window else window
	    flanks = [i for i, value in enumerate(stream) if abs(stream[i-1] - value) > final_window]
	    return sum([[flanks[i-1], val] for i, val in enumerate(flanks) if val - flanks[i - 1] > delay_time], [])

	def __get_normalized_audio(self):
	    if self.__stream is None:
	        pa = pyaudio.PyAudio()
	        self.__stream = pa.open(format=pyaudio.paInt16, channels=2, rate=self.__sampling_rate,
	                          		input=True, frames_per_buffer=self.__num_samples)
	    audio_data = np.fromstring(self.__stream.read(self.__num_samples), dtype=np.short)
	    audio_data = np.reshape(audio_data, (self.__num_samples, 2))

	    return audio_data / 32768.0

	def get_num_samples_per_period(self):
	    num_samples = 0
	    flanks = self.__get_stream_flanks(self.__get_normalized_audio()[:, 1])

	    if len(flanks) > 5:
	        num_samples = int(round(np.mean(map(lambda x, y: x-y, flanks[3:-2:2], flanks[2:-2:2]))))
	    return num_samples

	def get_audio_data(self, num_samples):
	    audio_data = self.__get_normalized_audio()

	    flanks = self.__get_stream_flanks(audio_data[:, 1])

	    if flanks:
	        length = int(round(np.mean(map(lambda x, y: x-y, flanks[1::2], flanks[0::2]))))
	        normalized_data = np.mean([audio_data[i:i+length] for i in flanks[2:-2:2]], axis=0)
	    else:
	        length = num_samples
	        normalized_data = audio_data[0:length]

	    return sign.Signal(normalized_data[:,0], fs=self.__sampling_rate)
