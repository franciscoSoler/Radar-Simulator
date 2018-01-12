from radarSignalAnalyzer.src.filters import ZccFilter, FftFilter

class DistanceCalculator:

    def __init__(self):
        self.__zcc_filter = ZccFilter()
        self.__fft_filter = FftFilter()

    @staticmethod
    def __calculate_distance(frequency, num_samples):
        return num_samples * C * frequency / (2*B * SAMPLING_RATE)

    def calculate_fft_distance(self, data, length):
        frequency = self.__fft_filter.calculate_frequency(data, length)
        self.distance_fft = self.__calculate_distance(frequency, len(data))

    def calculate_zcc_distance(self, data, flanks):
        frequency = self.__zcc_filter.calculate_frequency(data, flanks)
        num_samples = int(round(np.mean(map(lambda x, y: x-y, flanks[1::2], flanks[::2]))))
        self.distance_zcc = self.__calculate_distance(frequency, num_samples)

    def calculate_zcc_distance2(self, data):
        frequency = self.zcc_filter.calculate_frequency2(data)
        self.distance_zcc = self.__calculate_distance(float(frequency), len(data))
