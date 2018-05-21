import numpy as np

Spectrogram_length = 100
C = 299792458

F0 = 2434E6
BW = 290E6
Sampling_rate = 44100.

DELAY_TIME = 100

CONFIG_PATH = '../config/defaultParameters.xml'


def w2db(w):
    """Converts power [W] to dBs"""
    return -99999999999 if w == 0 else 10*np.log10(w)


def v2db(v):
    """Converts voltage [V] to dBs"""
    return 2*w2db(abs(v))


def db2v(dbs):
    """Converts dBs to voltage [V]"""
    return 10**(dbs/20)