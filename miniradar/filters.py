class ZccFilter:

    frequency = Float(0)

    def __init__(self):
        super(ZccFilter, self).__init__()
        self.__window = 0.1

    @staticmethod
    def __get_zero_crossings(data, delay_time=5):
        mean_data = np.mean(data)
        data2 = data - mean_data
        crossings = [i for i, value in enumerate(data2) if data2[i-1]*value < 0]
        return len([value for i, value in enumerate(crossings) if abs(value - crossings[i-1]) > delay_time])

    def calculate_frequency2(self, data):
        crossings = self.__get_zero_crossings(data)
        # print(crossings)
        freq = crossings/2. * SAMPLING_RATE/len(data)
        self.frequency = freq
        return freq

    def calculate_frequency(self, data, flanks):

        num_samples = map(lambda x, y: x-y, flanks[1::2], flanks[0::2])

        crossings_per_period = [self.__get_zero_crossings(data[flanks[2*i]:flanks[2*i]+period])
                                for i, period in enumerate(num_samples)]

        """
        data3 = np.concatenate([data[flanks[2*i]+CUT/2:flanks[2*i+1]-CUT/2] for i in range(len(flanks[::2]))], 1)
        # print(data3)
        crossings = self.__get_zero_crossings(data3, delay_time=10)
        freq = crossings * SAMPLING_RATE/(2*np.mean(num_samples)) / len(num_samples)
        """
        # print(crossings)
        # print(num_samples)
        # print(crossings_per_period)
        freq = np.mean([cross * SAMPLING_RATE/(2*num_samples[i]) for i, cross in enumerate(crossings_per_period)])
        self.frequency = freq
        return freq


class FftFilter:

    frequency = Float(0)

    def __init__(self):
        super(FftFilter, self).__init__()

    def calculate_frequency(self, data, length):
        # frequency = abs(fft(data[:length]))[:length/(2*FREQUENCY_DIVIDER)]

        freq = abs(fft(data[:length]))[:length/(2*FREQUENCY_DIVIDER)].argmax() * float(SAMPLING_RATE)/(
            # 2*FREQUENCY_DIVIDER)/((num_samples - CUT)/(2*FREQUENCY_DIVIDER)-1)
            2*FREQUENCY_DIVIDER)/(len(data)/(2*FREQUENCY_DIVIDER)-1)
        self.frequency = freq

        return freq
