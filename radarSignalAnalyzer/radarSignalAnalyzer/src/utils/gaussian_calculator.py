import numpy as np


class GaussianCalculator:

    def __init__(self):
        self.__n = 0
        self.__mean = 0
        self.__std = 0

    def clear(self):
        """Clear calculated mean and std."""
        self.__n = 0
        self.__mean = 0
        self.__std = 0

    def add_sample(self, sample):
        """Add a new sample updating the mean and std calculations."""
        new_mean = (self.__n * self.__mean + sample) / (self.__n + 1)

        if self.__n:
            self.__std = np.sqrt(((sample - new_mean)*(sample - self.__mean) + (self.__n - 1)*self.__std**2) / self.__n)

        self.__mean = new_mean
        self.__n += 1
        return self.__mean, self.__std

    def get_mean_std(self):
        return self.__mean, self.__std
