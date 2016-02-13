from filters import ZccFilter, FftFilter

class DistanceCalculator:

    distance_zcc = Float(0)
    distance_fft = Float(0)

    zcc_filter = Instance(ZccFilter, ())
    fft_filter = Instance(FftFilter, ())

    def __init__(self):
        super(DistanceCalculator, self).__init__()
        self.num_samples = 0

    @staticmethod
    def __calculate_distance(frequency, num_samples):
        return num_samples * C * frequency / (2*B * SAMPLING_RATE)

    def calculate_fft_distance(self, data, length):
        frequency = self.fft_filter.calculate_frequency(data, length)
        self.distance_fft = self.__calculate_distance(frequency, len(data))

    def calculate_zcc_distance(self, data, flanks):
        frequency = self.zcc_filter.calculate_frequency(data, flanks)
        num_samples = int(round(np.mean(map(lambda x, y: x-y, flanks[1::2], flanks[::2]))))
        self.distance_zcc = self.__calculate_distance(frequency, num_samples)

    def calculate_zcc_distance2(self, data):
        frequency = self.zcc_filter.calculate_frequency2(data)
        self.distance_zcc = self.__calculate_distance(float(frequency), len(data))
